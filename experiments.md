# Engineering Lab #3: Process Management & systemd Experiment Logs

## Experiment 1: Running Process Inspection

- **Action:** Executed `ps aux | grep heartbeat.py` and `pgrep -fl heartbeat.py`.
- **Expectation:** Locate the active Python worker process and retrieve its PID and owner.
- **Observation:** Process found running under PID `255` owned by non-root user `testpress`.
- **Explanation:** `ps` (**P**rocess **S**tatus) reads process state attributes directly from the `/proc` virtual filesystem (`/proc/255/status`).
- **Command Breakdown:**
  - `ps` (**P**rocess **S**tatus): Takes a snapshot of running processes.
  - `pgrep` (**P**rocess **Grep**): Searches processes using regular expressions (`-f` = Full command match, `-l` = List process name).
  - *Memory Trick:* **PS** = **P**rocess **S**napshot; **pgrep** = **P**rocess **Grep**.

## Experiment 2: Graceful Shutdown (SIGTERM)

- **Action:** Executed `kill -15 <PID>` (`pkill -SIGTERM -f heartbeat.py`).
- **Expectation:** Process catches signal 15, executes cleanup routine, and exits with code 0.
- **Observation:** Logged `Received signal SIGTERM (15). Shutting down gracefully...` followed by clean termination.
- **Explanation:** `SIGTERM` (**SIG**nal **TERM**inate) is a catchable signal. It requests process shutdown, allowing Python signal handlers (`signal.signal()`) to finish active tasks.
- **Command Breakdown:**
  - `kill -15`: Sends signal 15 (SIGTERM).
  - *Memory Trick:* Signal **15** is **F**riendly—it lets the application finish cleanup before leaving.

## Experiment 3: Forced Termination (SIGKILL)

- **Action:** Executed `kill -9 <PID>` (`pkill -SIGKILL -f heartbeat.py`).
- **Expectation:** Process is killed instantly by the kernel without running cleanup handlers.
- **Observation:** Process printed `Killed` instantly. No shutdown exit logs were generated.
- **Explanation:** `SIGKILL` (**SIG**nal **KILL**) bypasses process code entirely. It is handled directly by the kernel, which reclaims memory.
- **Command Breakdown:**
  - `kill -9`: Sends signal 9 (SIGKILL).
  - *Memory Trick:* Signal **9** has **N**o mercy—instant termination.

## Experiment 4: systemd Service Active

- **Action:** Executed `systemctl status testpress-worker.service`.
- **Expectation:** Service displays green `active (running)` state under `testpress` user with CGroup tracking.
- **Observation:** Service active with PID `255`, managed under `/system.slice/testpress-worker.service`.
- **Explanation:** systemd (PID 1) acts as the primary service orchestrator, tracking child processes using Linux kernel Control Groups (cgroups).
- **Command Breakdown:**
  - `systemctl` (**System Control**): The primary utility used to manage systemd services.
  - *Memory Trick:* **systemctl** = Control the **System** daemon.

## Experiment 5: Automatic Restart after Failure

- **Action:** Executed `sudo kill -9 <PID>` on an active systemd service.
- **Expectation:** systemd detects unexpected process death and automatically restarts it.
- **Observation:** Service automatically spawned under a new PID (e.g., PID `310`) after a 3-second delay.
- **Explanation:** `Restart=on-failure` inside the service unit instructs systemd to restart processes terminated by unhandled signals or non-zero exit codes.
- **Command Breakdown:**
  - `RestartSec=3s`: Sets the cooldown delay before systemd attempts a service restart.
  - *Memory Trick:* **on-failure** = Only restart when the app crashes unexpectedly (ignores clean exit code 0).

## Experiment 6: Crash Investigation with journalctl

- **Action:** Executed `journalctl -u testpress-worker.service -n 25`.
- **Expectation:** Inspect centralized systemd log streams to diagnose crash causes.
- **Observation:** Journal logs captured process death details: `Main process exited, code=killed, status=9/KILL`.
- **Explanation:** systemd attaches standard output (`stdout`) and standard error (`stderr`) streams to `systemd-journald`.
- **Command Breakdown:**
  - `journalctl` (**Journal Control**): Query tool for `systemd-journald`.
  - `-u` (**Unit**): Filters logs by unit name.
  - `-n` (**Number**): Limits log lines returned.
  - *Memory Trick:* **journalctl** = View system log **Journals**.

## Experiment 7: Invalid Configuration Handling

- **Action:** Updated `ExecStart` path to `/usr/bin/python3_invalid` and ran `systemctl restart testpress-worker.service`.
- **Expectation:** Service fails immediately during process launch.
- **Observation:** Unit entered `failed` state with error `status=203/EXEC`.
- **Explanation:** systemd uses the `execve()` system call to start binaries. If the target executable path does not exist, execution fails before the application starts.
- **Command Breakdown:**
  - `status=203/EXEC`: systemd execution failure code indicating the binary is missing or unexecutable.
  - *Memory Trick:* **203/EXEC** = **EXEC**ution failed before code could run.

## Experiment 8: Repeated Crash Rate Limiting

- **Action:** Set `SIMULATE_CRASH_AFTER=1` with `StartLimitBurst=3` and `StartLimitIntervalSec=30s`.
- **Expectation:** systemd locks the service to prevent endless crash-loop restarts.
- **Observation:** Unit entered `failed` state with error `start-limit-hit`.
- **Explanation:** Rate limiting prevents runaway processes from consuming CPU resources and flooding log storage during repeated failures.
- **Command Breakdown:**
  - `StartLimitBurst`: Maximum start attempts allowed within the interval window.
  - *Memory Trick:* **start-limit-hit** = Crash-loop circuit breaker triggered.

## Experiment 9: Resource Limits (OOM Killer)

- **Action:** Enabled memory allocation (`TRIGGER_OOM=true`) past the 50MB `MemoryMax` limit.
- **Expectation:** Linux Out-Of-Memory (OOM) killer terminates the process upon limit breach.
- **Observation:** Journal logged `A process of this unit has been killed by the OOM killer` with result `oom-kill`.
- **Explanation:** systemd sets memory boundaries using kernel cgroups v2 (`memory.max`). When RAM usage breaches the configured ceiling, the kernel can terminate the process using uncatchable `SIGKILL` (signal 9).
- **Command Breakdown:**
  - `MemoryMax=50M`: Hard memory limit enforced by kernel cgroups.
  - *Memory Trick:* **OOM** = **O**ut **O**f **M**emory.

## Experiment 10: Reboot Persistence

- **Action:** Terminated WSL (`wsl --shutdown`) from Windows host and reopened terminal.
- **Expectation:** systemd launches the worker automatically upon boot completion.
- **Observation:** Service displayed `active (running)` while system `uptime` showed `up 0 min`.
- **Explanation:** `WantedBy=multi-user.target` creates a symbolic link in `/etc/systemd/system/multi-user.target.wants/`, including the unit in the default boot targets.
- **Command Breakdown:**
  - `uptime`: Reports how long the OS kernel has been running.
  - `wsl --shutdown`: Completely shuts down the WSL virtual machine environment.
  - *Memory Trick:* **multi-user.target** = Standard multi-user startup target.
