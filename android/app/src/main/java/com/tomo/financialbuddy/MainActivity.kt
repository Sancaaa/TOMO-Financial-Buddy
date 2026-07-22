package com.tomo.financialbuddy

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Bitmap
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.webkit.*
import android.widget.ProgressBar
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

class MainActivity : AppCompatActivity() {

    companion object {
        private const val WEB_URL = "https://tomo.sanca.site"
        private const val ERROR_PAGE = "file:///android_asset/error.html"
    }

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private var isErrorShowing = false

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        progressBar = findViewById(R.id.progressBar)
        swipeRefresh = findViewById(R.id.swipeRefresh)

        // Configure SwipeRefreshLayout — tomato / leaf / gold spinner on warm paper
        swipeRefresh.setColorSchemeColors(
            resources.getColor(R.color.tomato, theme),
            resources.getColor(R.color.leaf, theme),
            resources.getColor(R.color.gold, theme)
        )
        swipeRefresh.setProgressBackgroundColorSchemeColor(
            resources.getColor(R.color.paper, theme)
        )
        swipeRefresh.setOnRefreshListener {
            if (isErrorShowing) {
                loadMainUrl()
            } else {
                webView.reload()
            }
        }

        // Configure WebView
        setupWebView()

        // Load the URL
        if (savedInstanceState == null) {
            loadMainUrl()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            allowFileAccess = true
            allowContentAccess = true
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            useWideViewPort = true
            loadWithOverviewMode = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            mediaPlaybackRequiresUserGesture = false
            
            // Enable service workers for PWA
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                safeBrowsingEnabled = true
            }
        }

        // ── Native-app feel ──────────────────────────────────────────────
        // Remove the browser-y "rubber-band" / edge glow when scrolling past
        // the top or bottom — this is the single biggest tell that it's a
        // WebView rather than a native screen.
        webView.overScrollMode = View.OVER_SCROLL_NEVER
        // No horizontal scrollbar (content is meant to fit the width).
        webView.isHorizontalScrollBarEnabled = false
        // Keep system font scaling from re-flowing the app's own type scale.
        webView.settings.textZoom = 100

        // Handle page navigation
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                if (url != ERROR_PAGE) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = 0
                }
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
                swipeRefresh.isRefreshing = false
                
                if (url != ERROR_PAGE) {
                    isErrorShowing = false
                    injectNativeFeel(view)
                }
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                super.onReceivedError(view, request, error)
                // Only show error page for main frame
                if (request?.isForMainFrame == true) {
                    showErrorPage()
                }
            }

            override fun onReceivedHttpError(
                view: WebView?,
                request: WebResourceRequest?,
                errorResponse: WebResourceResponse?
            ) {
                super.onReceivedHttpError(view, request, errorResponse)
                if (request?.isForMainFrame == true) {
                    val statusCode = errorResponse?.statusCode ?: 0
                    if (statusCode >= 500) {
                        showErrorPage()
                    }
                }
            }

            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val url = request?.url?.toString() ?: return false
                
                // Keep navigation within the app for the main domain
                return if (url.contains("tomo.sanca.site")) {
                    false // Let WebView handle it
                } else {
                    // Open external links in browser
                    try {
                        val intent = android.content.Intent(
                            android.content.Intent.ACTION_VIEW,
                            android.net.Uri.parse(url)
                        )
                        startActivity(intent)
                    } catch (e: Exception) {
                        // Ignore if no browser available
                    }
                    true
                }
            }
        }

        // Handle progress
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                super.onProgressChanged(view, newProgress)
                progressBar.progress = newProgress
                if (newProgress >= 100) {
                    progressBar.visibility = View.GONE
                }
            }
        }

        // Enable service worker support
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
            val serviceWorkerController = android.webkit.ServiceWorkerController.getInstance()
            serviceWorkerController.setServiceWorkerClient(object : android.webkit.ServiceWorkerClient() {
                override fun shouldInterceptRequest(request: WebResourceRequest?): WebResourceResponse? {
                    return null
                }
            })
        }
    }

    /**
     * Trims the remaining "web browser" behaviours the WebView flags can't reach:
     * locks the viewport scale (no pinch / double-tap zoom), kills the tap-highlight
     * flash and the long-press callout/selection magnifier, and disables overscroll
     * chaining — while still allowing text selection inside real input fields.
     */
    private fun injectNativeFeel(view: WebView?) {
        val js = """
            (function() {
              var vp = document.querySelector('meta[name=viewport]');
              if (!vp) { vp = document.createElement('meta'); vp.name = 'viewport'; document.head.appendChild(vp); }
              vp.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover');

              if (!document.getElementById('tomo-native-feel')) {
                var s = document.createElement('style');
                s.id = 'tomo-native-feel';
                s.textContent =
                  'html,body{overscroll-behavior:none;}' +
                  '*{-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none;}' +
                  '*:not(input):not(textarea):not([contenteditable]){-webkit-user-select:none;user-select:none;}';
                document.head.appendChild(s);
              }
            })();
        """.trimIndent()
        view?.evaluateJavascript(js, null)
    }

    private fun loadMainUrl() {
        if (isNetworkAvailable()) {
            isErrorShowing = false
            webView.loadUrl(WEB_URL)
        } else {
            showErrorPage()
        }
    }

    private fun showErrorPage() {
        isErrorShowing = true
        webView.loadUrl(ERROR_PAGE)
        progressBar.visibility = View.GONE
        swipeRefresh.isRefreshing = false
    }

    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            if (isErrorShowing) {
                // If showing error page, try to load main URL
                loadMainUrl()
                return true
            }
            if (webView.canGoBack()) {
                webView.goBack()
                return true
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        webView.restoreState(savedInstanceState)
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }

    override fun onPause() {
        super.onPause()
        webView.onPause()
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
