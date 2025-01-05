class ApplyStealth:
    page = None
    account = None

    def __init__(self, account, page):
        self.account = account
        self.page = page

    def init(self):
        (
            self.spoof_public_id()
            .spoof_automation_webdrive()
            .spoof_indexed_db()
            .spoof_local_storage()
            .spoof_storage_persisted()
            .spoof_plugins()
            .spoof_mime_types()
            .spoof_language()
            .spoof_media_devices()
            .spoof_battery()
            .spoof_permissions()
            .spoof_webgl_rendering_context()
            .spoof_media_codecs()
            .spoof_webrtc_ip_leak_protection()
            .spoof_hardware_concurrency()
            # .spoof_canvas()
            .spoof_webgl_rendering_context2()
            .spoof_fonts()
        )

    def spoof_public_id(self):
        self.page.add_init_script(r"""
               const fakeIP = '%s';

               Object.defineProperty(navigator, 'connection', {
                   value: { downlink: 10, effectiveType: '4g', rtt: 50, saveData: false },
               });

               const originalRTCPeerConnection = window.RTCPeerConnection;
               window.RTCPeerConnection = function (config) {
                   const pc = new originalRTCPeerConnection(config);
                   pc.addEventListener('icecandidate', event => {
                       if (event.candidate) {
                           const modifiedCandidate = event.candidate.candidate.replace(
                               /(?:[0-9]{1,3}\.){3}[0-9]{1,3}/g, fakeIP
                           );
                           Object.defineProperty(event.candidate, 'candidate', {
                               value: modifiedCandidate,
                           });
                       }
                   });
                   return pc;
               };
           """ % self.account.proxy.ip)

        return self

    def spoof_automation_webdrive(self):
        self.page.add_init_script("""
                         navigator.webdriver = false
                         Object.defineProperty(navigator, 'webdriver', {
                             get: () => false
                         })
                     """)
        return self

    def spoof_indexed_db(self):
        self.page.add_init_script("""
                  const originalIndexedDB = window.indexedDB;
                  Object.defineProperty(window, 'indexedDB', {
                      get: () => originalIndexedDB
                  });
              """)
        return self

    def spoof_local_storage(self):
        self.page.add_init_script("""
                   Object.defineProperty(window, 'localStorage', {
                       get: () => ({
                           length: 0,
                           getItem: () => null,
                           setItem: () => {},
                           removeItem: () => {},
                           clear: () => {}
                       })
                   });

                   Object.defineProperty(window, 'sessionStorage', {
                       get: () => ({
                           length: 0,
                           getItem: () => null,
                           setItem: () => {},
                           removeItem: () => {},
                           clear: () => {}
                       })
                   });
               """)
        return self

    def spoof_storage_persisted(self):
        self.page.add_init_script("""
                   Object.defineProperty(window.navigator, 'storage', {
                       value: {
                           persisted: () => Promise.resolve(false)
                       }
                   });
               """)
        return self

    def spoof_plugins(self):
        self.page.add_init_script("""
                       Object.defineProperty(navigator, 'plugins', {
                           get: () => [
                               { name: 'PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                               { name: 'Chrome PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                               { name: 'Microsoft Edge PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' }
                           ]
                       });
                   """)
        return self

    def spoof_mime_types(self):
        self.page.add_init_script("""
                               Object.defineProperty(navigator, 'mimeTypes', {
                                   get: () => [
                                       { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                                       { type: 'text/pdf', suffixes: 'pdf', description: 'Portable Document Format' }
                                   ]
                               });
                           """)
        return self

    def spoof_language(self):
        self.page.add_init_script("""
                  Object.defineProperty(navigator, 'languages', {
                      get: () => ['en-US', 'en']
                  });
                  """)
        return self

    def spoof_media_devices(self):
        self.page.add_init_script("""
                      Object.defineProperty(navigator, 'mediaDevices', {
                          get: () => ({
                              enumerateDevices: () => Promise.resolve([
                                  { kind: 'audioinput', label: 'Microphone', deviceId: 'default' },
                                  { kind: 'videoinput', label: 'Webcam', deviceId: 'default' }
                              ])
                          })
                      });
                  """)
        return self

    def spoof_battery(self):
        self.page.add_init_script("""
                  navigator.getBattery = () => Promise.resolve({
                      charging: true,
                      chargingTime: 0,
                      dischargingTime: Infinity,
                      level: 1
                  });
                  """)
        return self

    def spoof_permissions(self):
        self.page.add_init_script("""
                   const originalQuery = window.navigator.permissions.query;
                   window.navigator.permissions.query = (parameters) => (
                       parameters.name === 'notifications' ?
                       Promise.resolve({ state: Notification.permission }) :
                       originalQuery(parameters)
                   );
                   """)
        return self

    def spoof_webgl_rendering_context(self):
        self.page.add_init_script("""
               const getParameter = WebGLRenderingContext.prototype.getParameter;
               WebGLRenderingContext.prototype.getParameter = function(parameter) {
                   if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                       return "Google Inc."; // Vendor value
                   }
                   if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                       return "ANGLE (NVIDIA GeForce RTX 2080 Direct3D11 vs_5_0 ps_5_0, D3D11)"; // Renderer value
                   }
                   return getParameter.call(this, parameter);
               };

               const getSupportedExtensions = WebGLRenderingContext.prototype.getSupportedExtensions;
               WebGLRenderingContext.prototype.getSupportedExtensions = function() {
                   return [
                       "EXT_texture_filter_anisotropic",
                       "EXT_color_buffer_half_float",
                       "WEBGL_debug_renderer_info",
                       "WEBGL_lose_context",
                       "EXT_blend_minmax",
                       "EXT_disjoint_timer_query",
                       "EXT_frag_depth",
                       "OES_element_index_uint",
                       "OES_fbo_render_mipmap",
                       "OES_standard_derivatives",
                       "OES_texture_float",
                       "OES_texture_float_linear",
                       "OES_texture_half_float",
                       "OES_texture_half_float_linear",
                       "OES_vertex_array_object",
                       "WEBGL_compressed_texture_s3tc",
                       "WEBGL_compressed_texture_s3tc_srgb"
                   ];
               };
           """)
        return self

    def spoof_media_codecs(self):
        self.page.add_init_script("""
                 const canPlayType = HTMLMediaElement.prototype.canPlayType;
                 HTMLMediaElement.prototype.canPlayType = function(type) {
                     if (type === 'audio/mpeg') return 'probably';
                     if (type === 'audio/ogg') return 'probably';
                     if (type === 'video/mp4') return 'probably';
                     if (type === 'video/webm') return 'probably';
                     return '';
                 };
                 """)
        return self

    def spoof_webrtc_ip_leak_protection(self):
        self.page.add_init_script("""
                  const getParameter = RTCPeerConnection.prototype.getParameters;
                  RTCPeerConnection.prototype.getParameters = function() {
                      return { iceServers: [] };
                  };
                  """)
        return self

    def spoof_hardware_concurrency(self):
        self.page.add_init_script("""
                  Object.defineProperty(navigator, 'hardwareConcurrency', {
                      get: () => 16  
                  });
                  """)
        return self

    def spoof_canvas(self):
        self.page.add_init_script("""
                      const originalGetContext = HTMLCanvasElement.prototype.getContext;
                      HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                          const context = originalGetContext.call(this, type, attributes);
                          if (type === '2d') {
                              const originalGetImageData = context.getImageData;
                              context.getImageData = function(x, y, width, height) {
                                  const imageData = originalGetImageData.call(this, x, y, width, height);
                                  for (let i = 0; i < imageData.data.length; i += 4) {
                                      imageData.data[i] = imageData.data[i] ^ 255; // Invert color
                                  }
                                  return imageData;
                              };
                          }
                          return context;
                      };
                  """)
        return self

    def spoof_webgl_rendering_context2(self):
        self.page.add_init_script("""
                   const originalGetContextAttributes = WebGLRenderingContext.prototype.getContextAttributes;
                   WebGLRenderingContext.prototype.getContextAttributes = function() {
                       const attributes = originalGetContextAttributes.call(this);
                       attributes.antialias = true;
                       attributes.alpha = true;
                       attributes.depth = true;
                       attributes.stencil = false;
                       attributes.premultipliedAlpha = true;
                       attributes.preserveDrawingBuffer = false;
                       return attributes;
                   };
               """)
        return self

    def spoof_fonts(self):
        self.page.add_init_script("""
                     Object.defineProperty(document, 'fonts', {
                         get: () => ({
                             add: () => {},
                             delete: () => {},
                             clear: () => {},
                             check: () => true,
                             load: () => Promise.resolve([]),
                             ready: Promise.resolve([])
                         })
                     });
                 """)
        return self
