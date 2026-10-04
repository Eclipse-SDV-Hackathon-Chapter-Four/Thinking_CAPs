FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$PATH:/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:/opt/android-sdk/emulator"

# ---------------------------------------------------------
# 1. Basic dependencies
# ---------------------------------------------------------
RUN apt-get update && apt-get install -y \
    wget unzip curl git sudo lib32stdc++6 lib32z1 \
    qemu-kvm libvirt-daemon-system libvirt-clients \
    aapt \
    libglu1-mesa \
    openjdk-17-jdk \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# 2. Install Android SDK (cmdline-tools) - NO ANDROID STUDIO
# ---------------------------------------------------------
RUN mkdir -p $ANDROID_HOME/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline.zip && \
    unzip cmdline.zip -d $ANDROID_HOME/cmdline-tools && \
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest && \
    rm cmdline.zip

# ---------------------------------------------------------
# 3. Install essential SDK components
# ---------------------------------------------------------
RUN yes | sdkmanager --licenses

RUN sdkmanager \
    "platform-tools" \
    "emulator" \
    "platforms;android-34" \
    "system-images;android-34;google_apis;x86_64" \
    "build-tools;34.0.0"

# ---------------------------------------------------------
# 4. Create Pixel Tablet–like AVD
# ---------------------------------------------------------
RUN echo "no" | avdmanager create avd \
    --name pixel_tablet_api34 \
    --package "system-images;android-34;google_apis;x86_64" \
    --device "Nexus 7" \
    --abi "x86_64"

# Override device hardware to mimic Pixel Tablet specs.
RUN mkdir -p /root/.android/avd/pixel_tablet_api34.avd && \
    printf "\
hw.lcd.width=2560\n\
hw.lcd.height=1600\n\
hw.lcd.depth=16\n\
hw.lcd.density=200\n\
hw.lcd.size=10.95\n\
hw.lcd.dpi=276\n\
hw.device.name=PixelTablet\n\
hw.device.manufacturer=Google\n\
hw.gpu.enabled=yes\n\
hw.gpu.mode=auto\n\
vm.heapSize=512\n\
" >> /root/.android/avd/pixel_tablet_api34.avd/config.ini

# ---------------------------------------------------------
# 5. Runtime environment
# ---------------------------------------------------------
ENV QT_X11_NO_MITSHM=1

# ---------------------------------------------------------
# 6. Copy run_apk.sh to container and make it executable
# ---------------------------------------------------------
COPY run_apk.sh /opt/run_apk.sh
RUN chmod +x /opt/run_apk.sh

# Keep container alive
CMD ["/bin/bash", "-c", "tail -f /dev/null"]
