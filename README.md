# Testpress Linux Process Management & systemd Worker

A lightweight Python background worker managed by `systemd` featuring signal trapping, CGroup memory ceilings, crash rate-limiting, and automated recovery.

## 📁 Repository Structure

```text
.
├── heartbeat.py                # Worker source code (SIGTERM/SIGINT handling & OOM test hook)
├── testpress-worker.service    # systemd unit file (non-root user, limits & restart policy)
├── testpress-worker.env        # Service environment variables
├── experiments.md              # Documentation for 10 mandatory lab experiments
└── evidence/                   # 10 execution evidence screenshots
```

## 📍 Directory Standards: Where Files Belong & Why

| **File Type** | **Standard System Path** | **Purpose** |
|---|---|---|
| **Service Unit File** | `/etc/systemd/system/testpress-worker.service` | System-wide service configuration managed by system administrator. |
| **App & Config Files** | `/opt/testpress-worker/` | Dedicated directory for third-party application binaries and `.env` files. |
| **System Log Storage** | `/var/log/journal/` | Binary storage location for system logs managed by `systemd-journald`. |

## 📡 Linux Signals & Behavior Reference

| **Signal** | **Number** | **Catchable?** | **Purpose & Application Behavior** |
|---|---|---|---|
| **`SIGINT`** | `2` | ✅ Yes | **Interrupt:** Triggered by `Ctrl+C`. Used for manual terminal interruptions. |
| **`SIGKILL`** | `9` | ❌ No | **Force Kill:** Processed directly by kernel. Instant termination, zero cleanup. |
| **`SIGTERM`** | `15` | ✅ Yes | **Terminate:** Standard stop request sent by `systemd` or `kill`. Allows clean shutdown. |

## 🚀 Key Service Management Commands

### Start and enable service on boot

```bash
sudo systemctl enable --now testpress-worker.service
```

### Check active status and CGroup allocation

```bash
systemctl status testpress-worker.service
```

### Stream real-time logs

```bash
journalctl -u testpress-worker.service -f
```

## 🔍 Diagnostic & Troubleshooting Toolkit

| **Problem** | **Diagnostic Command** | **What to Look For** |
|---|---|---|
| **Service Crashed / Failed** | `systemctl status testpress-worker.service` | Look at `Active:` state and `Main PID` exit code. |
| **Investigate Error Logs** | `journalctl -u testpress-worker.service -n 50` | Displays the last 50 error and console log outputs. |
| **Trace Crash Loops** | `journalctl -u testpress-worker.service --since "10 min ago"` | Shows frequency of restarts and rate-limiting alerts. |
| **Verify Resource Usage** | `systemctl show testpress-worker.service -p MemoryCurrent,CPUUsageNSec` | Inspect exact RAM bytes and CPU runtime used by CGroup. |
| **Clear Rate-Limit Locks** | `sudo systemctl reset-failed testpress-worker.service` | Clears `start-limit-hit` lockouts so the service can restart. |

## 🧪 Verified Experiments Summary

| **Exp** | **Test Case** | **Observed Result** | **Key Mechanism** |
|---|---|---|---|
| **1** | Process Inspection | PID tracked under `testpress` user | `/proc/<PID>/status` |
| **2** | `SIGTERM` Shutdown | Clean exit with code `0` | Signal 15 handler |
| **3** | `SIGKILL` Kill | Instant termination (`Killed`) | Signal 9 (Kernel level) |
| **4** | Active Service | Status: `active (running)` | `systemd` CGroup tracking |
| **5** | Auto Restart | New PID assigned on crash | `Restart=on-failure` |
| **6** | Log Diagnostics | Exit captured in `journalctl` | `stdout`/`stderr` logging |
| **7** | Invalid Exec | Failed with status `203/EXEC` | `execve()` system call failure |
| **8** | Crash Rate Limit | Locked with `start-limit-hit` | `StartLimitBurst=3` threshold |
| **9** | OOM Memory Cap | Killed by kernel OOM killer | `MemoryMax=50M` CGroup limit |
| **10** | Reboot Persistence | Auto-started after system boot | `multi-user.target` link |
