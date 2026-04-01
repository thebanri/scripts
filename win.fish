#!/bin/bash
# win - Reboot into Windows via Limine boot order change
# Usage: win
#
# Uses --bootorder instead of --bootnext to keep the EFI boot path
# consistent. This prevents TPM PCR values from changing, which would
# otherwise cause Windows to invalidate the PIN on every boot.

set -euo pipefail

WINDOWS_BOOT_ENTRY="0000"
LINUX_BOOT_ORDER="0004,0000,0001,0005"

echo "Setting Windows (Boot${WINDOWS_BOOT_ENTRY}) as first in boot order..."

# Build new boot order with Windows first, keeping the rest in original order
NEW_ORDER="${WINDOWS_BOOT_ENTRY},$(echo "$LINUX_BOOT_ORDER" | sed "s/${WINDOWS_BOOT_ENTRY},\?//;s/,$//")"

sudo efibootmgr --bootorder "$NEW_ORDER" > /dev/null

# Schedule restoration of original boot order for next Linux boot
RESTORE_SCRIPT="/tmp/restore-boot-order.sh"
cat > "$RESTORE_SCRIPT" << 'RESTORE'
#!/bin/bash
efibootmgr --bootorder "0004,0000,0001,0005" > /dev/null 2>&1
RESTORE
chmod +x "$RESTORE_SCRIPT"

# Create a one-shot systemd service to restore boot order on next Linux boot
sudo tee /etc/systemd/system/restore-boot-order.service > /dev/null << EOF
[Unit]
Description=Restore EFI boot order after Windows reboot
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/efibootmgr --bootorder $LINUX_BOOT_ORDER
ExecStartPost=/bin/systemctl disable restore-boot-order.service

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable restore-boot-order.service > /dev/null 2>&1

echo "Boot order set to: $NEW_ORDER"
echo "Original order ($LINUX_BOOT_ORDER) will be restored on next Linux boot."
echo "Rebooting into Windows..."
sudo systemctl reboot
