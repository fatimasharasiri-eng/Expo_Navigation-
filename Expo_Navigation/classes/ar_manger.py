import html
import streamlit.components.v1 as components


class ARManager:

    def camera_view(
        self,
        target_bearing=0,
        next_name="Main Corridor",
        next_distance=20,
        destination="Destination",
        north_offset=0
    ):
        """Camera view with an arrow that rotates with the phone's compass.

        target_bearing : direction (degrees, 0 = north, clockwise) of the next stop
        north_offset   : calibration (degrees) added to target_bearing, to match
                         the map's north with the real north
        """

        destination = html.escape(str(destination))
        next_name = html.escape(str(next_name))
        next_distance = html.escape(str(next_distance))

        try:
            bearing_value = float(target_bearing)
        except (TypeError, ValueError):
            bearing_value = 0.0
        try:
            offset_value = float(north_offset)
        except (TypeError, ValueError):
            offset_value = 0.0

        html_code = """
        <!DOCTYPE html>
        <html>

        <head>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    padding: 10px;
                    background: #F5F7F4;
                    font-family: Arial, sans-serif;
                    color: #173D32;
                }

                .header {
                    font-size: 25px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }

                .subtitle {
                    color: #68776F;
                    font-size: 14px;
                    margin-bottom: 15px;
                }

                .info-card {
                    background: white;
                    border-radius: 14px;
                    padding: 16px;
                    margin-bottom: 15px;
                    border: 1px solid #E1E9E3;
                }

                .label {
                    font-size: 12px;
                    color: #658273;
                    font-weight: bold;
                    margin-bottom: 5px;
                }

                .value {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 12px;
                    color: #173D32;
                }

                .camera-container {
                    position: relative;
                    width: 100%;
                    height: 430px;
                    background: #17231D;
                    border-radius: 16px;
                    overflow: hidden;
                }

                video {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: none;
                }

                .placeholder {
                    position: absolute;
                    inset: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    text-align: center;
                    gap: 12px;
                }

                .camera-icon {
                    font-size: 48px;
                }

                .guidance {
    display: none;
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: transparent;
    color: white;
    padding: 0;
    text-align: center;
    min-width: 180px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
}

.arrow {
    display: block;
    font-size: 65px;
    line-height: 1.1;
    color: #FAF6EE;
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.8));
    transform-origin: 50% 50%;
    transition: transform 0.12s linear;
    will-change: transform;
}

                .direction-text {
                    font-size: 16px;
                    font-weight: bold;
                }

                .state-card {
                    background: white;
                    border: 1px solid #E1E9E3;
                    border-radius: 14px;
                    padding: 20px;
                    text-align: center;
                    margin-top: 15px;
                }

                .state-icon {
                    font-size: 35px;
                    margin-bottom: 8px;
                }

                .state-title {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }

                .state-message {
                    color: #68776F;
                    font-size: 13px;
                    line-height: 1.6;
                    margin-bottom: 15px;
                }

                button {
                    background: #38765B;
                    color: white;
                    border: none;
                    padding: 14px 20px;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                    max-width: 300px;
                    margin: 5px;
                }

                button:disabled {
                    opacity: 0.6;
                    cursor: wait;
                }

                .stop-button {
                    background: #A83252;
                    display: none;
                }

                .status {
                    color: #38765B;
                    font-size: 12px;
                    margin-top: 10px;
                    overflow-wrap: anywhere;
                }

                @media (max-width: 600px) {

                    .camera-container {
                        height: 380px;
                    }

                    body {
                        padding: 5px;
                    }

                    .header {
                        font-size: 21px;
                    }

                }

            </style>

        </head>

        <body>

            <div class="header">
                EXORA AR Navigation
            </div>

            <div class="subtitle">
                Follow the arrow to reach your destination.
            </div>

            <div class="info-card">

                <div class="label">
                    YOUR DESTINATION
                </div>

                <div class="value">
                    __DESTINATION__
                </div>

                <hr>

                <div class="label">
                    NEXT LOCATION
                </div>

                <div class="value">
                    __NEXT_NAME__
                </div>

                <div class="label">
                    DISTANCE
                </div>

                <div class="value">
                    __NEXT_DISTANCE__ meters
                </div>

            </div>

            <div class="camera-container">

                <video id="camera"
                       autoplay
                       playsinline
                       muted>
                </video>

                <div class="placeholder" id="placeholder">

                    <div class="camera-icon">📷</div>

                    <div>
                        Camera is ready
                    </div>

                    <div>
                        Press Start AR Navigation
                    </div>

                </div>

                <div class="guidance" id="guidance">

                    <span class="arrow" id="arrow">↑</span>

                    <span class="direction-text" id="directionText">
                        Go Straight
                    </span>

                </div>

            </div>

            <div class="state-card">

                <div class="state-icon" id="stateIcon">
                    🧭
                </div>

                <div class="state-title" id="stateTitle">
                    AR Guidance
                </div>

                <div class="state-message" id="stateMessage">
                    Start navigation to activate your camera.
                </div>

                <button id="startButton">
                    Start AR Navigation
                </button>

                <button id="stopButton" class="stop-button">
                    Stop Navigation
                </button>

                <div class="status" id="status"></div>

            </div>


            <script>

                const video = document.getElementById("camera");

                const placeholder =
                    document.getElementById("placeholder");

                const guidance =
                    document.getElementById("guidance");

                const startButton =
                    document.getElementById("startButton");

                const stopButton =
                    document.getElementById("stopButton");

                const stateIcon =
                    document.getElementById("stateIcon");

                const stateTitle =
                    document.getElementById("stateTitle");

                const stateMessage =
                    document.getElementById("stateMessage");

                const status =
                    document.getElementById("status");

                const arrowEl =
                    document.getElementById("arrow");

                const directionText =
                    document.getElementById("directionText");

                let cameraStream = null;


                /* ---------------- compass ---------------- */

                const TARGET_BEARING = __TARGET_BEARING__ + __NORTH_OFFSET__;

                let smoothHeading = null;
                let gotAbsolute = false;
                let compassOn = false;


                // heading of the back of the phone (the camera), tilt-compensated
                function tiltCompensatedHeading(alpha, beta, gamma) {

                    const d = Math.PI / 180;
                    const a = alpha * d;
                    const b = beta * d;
                    const g = gamma * d;

                    const cA = Math.cos(a);
                    const sA = Math.sin(a);
                    const sB = Math.sin(b);
                    const cG = Math.cos(g);
                    const sG = Math.sin(g);

                    const rA = -cA * sG - sA * sB * cG;
                    const rB = -sA * sG + cA * sB * cG;

                    let h = Math.atan(rA / rB);

                    if (rB < 0) {
                        h += Math.PI;
                    } else if (rA < 0) {
                        h += 2 * Math.PI;
                    }

                    return h / d;

                }


                function onOrientation(e) {

                    let heading = null;

                    if (
                        e.webkitCompassHeading !== undefined &&
                        e.webkitCompassHeading !== null
                    ) {

                        // iOS
                        heading = e.webkitCompassHeading;

                    } else if (
                        e.alpha !== null &&
                        e.beta !== null &&
                        e.gamma !== null
                    ) {

                        // Android: prefer the absolute (magnetic) event
                        if (e.type === "deviceorientationabsolute") {
                            gotAbsolute = true;
                        } else if (gotAbsolute) {
                            return;
                        }

                        heading = tiltCompensatedHeading(
                            e.alpha,
                            e.beta,
                            e.gamma
                        );

                    }

                    if (heading === null || isNaN(heading)) {
                        return;
                    }

                    // smooth the movement (handles the 359 -> 0 jump)
                    if (smoothHeading === null) {

                        smoothHeading = heading;

                    } else {

                        const diff =
                            ((heading - smoothHeading + 540) % 360) - 180;

                        smoothHeading =
                            (smoothHeading + diff * 0.2 + 360) % 360;

                    }

                    // angle between where the phone points and the target: -180..180
                    const rel =
                        (((TARGET_BEARING - smoothHeading) % 360 + 540) % 360) - 180;

                    arrowEl.style.transform = "rotate(" + rel + "deg)";

                    const abs = Math.abs(rel);

                    if (abs < 20) {
                        directionText.textContent = "Go Straight";
                    } else if (abs > 150) {
                        directionText.textContent = "Turn Around";
                    } else if (rel > 0) {
                        directionText.textContent = "Turn Right";
                    } else {
                        directionText.textContent = "Turn Left";
                    }

                }


                async function enableCompass() {

                    if (compassOn) {
                        return true;
                    }

                    try {

                        // iOS needs permission, and it must be asked from a tap
                        if (
                            typeof DeviceOrientationEvent !== "undefined" &&
                            typeof DeviceOrientationEvent.requestPermission === "function"
                        ) {

                            const permission =
                                await DeviceOrientationEvent.requestPermission();

                            if (permission !== "granted") {
                                return false;
                            }

                        }

                        window.addEventListener(
                            "deviceorientationabsolute",
                            onOrientation,
                            true
                        );

                        window.addEventListener(
                            "deviceorientation",
                            onOrientation,
                            true
                        );

                        compassOn = true;
                        return true;

                    } catch (compassError) {

                        console.error("Compass Error:", compassError);
                        return false;

                    }

                }


                function disableCompass() {

                    window.removeEventListener(
                        "deviceorientationabsolute",
                        onOrientation,
                        true
                    );

                    window.removeEventListener(
                        "deviceorientation",
                        onOrientation,
                        true
                    );

                    compassOn = false;
                    smoothHeading = null;
                    gotAbsolute = false;

                    arrowEl.style.transform = "rotate(0deg)";
                    directionText.textContent = "Go Straight";

                }


                /* ---------------- camera ---------------- */

                function showState(title, icon, message) {

                    stateTitle.textContent = title;
                    stateIcon.textContent = icon;
                    stateMessage.textContent = message;

                }


                async function startNavigation() {

                    startButton.disabled = true;

                    // must be the first await after the tap (iOS permission rule)
                    const compassOk = await enableCompass();

                    try {

                        if (!window.isSecureContext) {

                            throw new Error(
                                "HTTPS is required to access the camera."
                            );

                        }

                        if (
                            !navigator.mediaDevices ||
                            !navigator.mediaDevices.getUserMedia
                        ) {

                            throw new Error(
                                "Camera is not supported by this browser."
                            );

                        }

                        showState(
                            "Starting Camera",
                            "📷",
                            "Please allow camera access."
                        );

                        status.textContent =
                            "Requesting camera permission...";


                        try {

                            cameraStream =
                                await navigator.mediaDevices.getUserMedia({

                                    video: {
                                        facingMode: {
                                            ideal: "environment"
                                        },
                                        width: {
                                            ideal: 1280
                                        },
                                        height: {
                                            ideal: 720
                                        }
                                    },

                                    audio: false

                                });

                        } catch (firstError) {

                            cameraStream =
                                await navigator.mediaDevices.getUserMedia({

                                    video: true,
                                    audio: false

                                });

                        }


                        video.srcObject = cameraStream;

                        video.setAttribute("playsinline", "");
                        video.setAttribute("autoplay", "");
                        video.muted = true;

                        video.style.display = "block";

                        await video.play();

                        placeholder.style.display = "none";
                        guidance.style.display = "block";

                        showState(
                            "AR Navigation Active",
                            "🧭",
                            "Follow the arrow to reach your destination."
                        );

                        status.textContent = compassOk
                            ? "Camera and compass are active."
                            : "Camera is active (compass unavailable).";

                        startButton.style.display = "none";
                        stopButton.style.display = "inline-block";


                    } catch (error) {

                        console.error("Camera Error:", error);

                        stopCamera();

                        showState(
                            "Camera Error",
                            "⚠️",
                            error.message
                        );

                        status.textContent =
                            error.name + ": " + error.message;

                    } finally {

                        startButton.disabled = false;

                    }

                }


                function stopCamera() {

                    if (cameraStream) {

                        cameraStream.getTracks().forEach(track => {
                            track.stop();
                        });

                        cameraStream = null;

                    }

                    disableCompass();

                    video.pause();
                    video.srcObject = null;
                    video.style.display = "none";

                    placeholder.style.display = "flex";
                    guidance.style.display = "none";

                    startButton.style.display = "inline-block";
                    stopButton.style.display = "none";

                }


                startButton.addEventListener(
                    "click",
                    startNavigation
                );


                stopButton.addEventListener("click", () => {

                    stopCamera();

                    showState(
                        "Navigation Stopped",
                        "🧭",
                        "You can start navigation again."
                    );

                    status.textContent = "Camera stopped.";

                });


            </script>

        </body>

        </html>
        """

        html_code = (
            html_code
            .replace("__DESTINATION__", destination)
            .replace("__NEXT_NAME__", next_name)
            .replace("__NEXT_DISTANCE__", next_distance)
            .replace("__TARGET_BEARING__", repr(bearing_value))
            .replace("__NORTH_OFFSET__", repr(offset_value))
        )

        components.html(
            html_code,
            height=850,
            scrolling=True
        )