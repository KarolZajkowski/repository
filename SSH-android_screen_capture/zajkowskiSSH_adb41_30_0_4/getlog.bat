::kwx935638
:: If is there need to use new future bat file, then rename this folder name to 'getlog.bat'
:: Always add %adb% for Android Debug Bridge and select device typing -s %sn%

echo off
echo  Remember about the SPACE in the command-line interpreter- it shouldn't be in the path


set Folder=%1
set sn=%2
set adb=%3
mkdir %Folder%


%adb% -s %sn% exec-out screencap -p > %Folder%\screen.png


%adb% -s %sn% root
%adb% -s %sn% shell "echo 3 > /proc/sys/vm/drop_caches"
%adb% -s %sn% shell echo 1 /sys/kernel/debug/tracing/events/gpu/enable
%adb% -s %sn% shell echo 1 /sys/kernel/debug/tracing/events/irq/enable
%adb% -s %sn% shell echo 1 /sys/kernel/debug/tracing/events/sched_wakeup/enable
%adb% -s %sn% shell echo 1 /sys/kernel/debug/tracing/events/sched_wakeup_new/enable
%adb% -s %sn% shell "echo 1 >/sys/kernel/debug/tracing/events/binder/binder_transaction_received/enable"
%adb% -s %sn% shell "echo 1 >/sys/kernel/debug/tracing/events/binder/binder_transaction/enable"
%adb% -s %sn% shell "echo 2048 > /sys/kernel/debug/tracing/saved_cmdlines_size"


%adb% -s %sn% shell  cat /sys/kernel/debug/boardid/boardid > %Folder%\boardid.txt
%adb% -s %sn% shell  cat /sys/kernel/debug/boardid/common/common > %Folder%\boardid_common.txt
%adb% -s %sn% shell  dmesg > %Folder%\dmesg.txt
%adb% -s %sn% shell ps > %Folder%\ps.txt

%adb% -s %sn% shell  logcat -v time -d -b radio > %Folder%\logcat_ril.txt
%adb% -s %sn% shell  logcat -v time -d -b radio -s AT > %Folder%\logcat_at.txt
%adb% -s %sn% shell  logcat -v time -d > %Folder%\logcat.txt

%adb% -s %sn% pull   /data/logs   %Folder%/logs_all.txt

mkdir %Folder%\android_logs
%adb% -s %sn% pull   /data/log/android_logs  %Folder%/android_logs

mkdir %Folder%\dumplog
%adb% -s %sn% pull   /data/dumplog %Folder%\dumplog

mkdir %Folder%\dontpanic
%adb% -s %sn% pull   /data/dontpanic %Folder%\dontpanic\

mkdir %Folder%\dropbox
%adb% -s %sn% pull   /data/system/dropbox         %Folder%\dropbox

mkdir %Folder%\tombstones
%adb% -s %sn% pull   /data/tombstones             %Folder%\tombstones

mkdir %Folder%\anr
%adb% -s %sn% pull   /data/anr                    %Folder%\anr

mkdir %Folder%\jank
%adb% -s %sn% pull   /data/log/jank           %Folder%\jank

mkdir %Folder%\dumpsys_meminfo
%adb% -s %sn% shell dumpsys meminfo > %Folder%\dumpsys_meminfo\info.txt


%adb% -s %sn% shell dumpsys jobscheduler > %Folder%/jobscheduler.txt
%adb% -s %sn% shell  bugreport > %Folder%/bug_report.txt


::%adb% shell "cat /etc/bluetooth/bt_stack.conf | grep FileName"
mkdir %Folder%\bt
%adb% -s %sn% pull   /data/log/bt                   %Folder%\bt



%adb% -s %sn% shell "rm /data/dontpanic/*"
%adb% -s %sn% shell "rm /data/system/dropbox/*"
%adb% -s %sn% shell "rm /data/corefile/*"
%adb% -s %sn% shell "rm /data/tombstones/*"
%adb% -s %sn% shell "rm /data/anr/*"
%adb% -s %sn% shell "rm /data/log/jank*"
%adb% -s %sn% shell "rm /data/android_logs/*"
%adb% -s %sn% shell "rm -rR /data/log/android_logs/*.*"
%adb% -s %sn% shell "rm -rR /data/log/bt/*.*"



echo            log collection complete
echo -------------------------------------------------
echo