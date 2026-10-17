FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      live-build debootstrap xorriso squashfs-tools grub-pc-bin grub-efi-amd64-bin \
      syslinux syslinux-common isolinux mtools dosfstools ca-certificates \
      gcc-mingw-w64-x86-64 gcc-mingw-w64-i686 \
      qemu-system-x86 ovmf socat shellcheck make \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
