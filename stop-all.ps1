<#
    校园文创产品生产管理系统 —— 停止脚本
    只停本项目的进程，不动 MySQL（系统服务），Redis 需显式加 -IncludeRedis

    用法：
        .\stop-all.ps1                 # 停引擎 + nginx + 授权服务
        .\stop-all.ps1 -IncludeRedis   # 连 Redis 一起停
#>
[CmdletBinding()]
param(
    [switch]$IncludeRedis
)

$root = $PSScriptRoot
$NginxDir = Join-Path $root '.runtime\nginx-windows\nginx-1.30.6-windows'
$NginxExe = Join-Path $NginxDir 'nginx.exe'
$BackendDir = Join-Path $root 'iidp-backend-demo'
$EngineJarName = 'sie-iidp-demo-start-1.0-SNAPSHOT.jar'

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    OK  $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "    !!  $msg" -ForegroundColor Yellow }

Write-Host "`n校园文创产品生产管理系统 · 停止`n" -ForegroundColor White

# ---------- nginx ----------
Write-Step 'nginx (30666)'
if (Test-Path $NginxExe) {
    Push-Location $NginxDir
    try { & $NginxExe -s quit 2>$null } catch { }
    Pop-Location
    Start-Sleep -Seconds 2
}
$nginx = Get-Process nginx -ErrorAction SilentlyContinue
if ($nginx) {
    $nginx | Stop-Process -Force
    Write-Ok '已强制结束 nginx 进程'
} else { Write-Ok 'nginx 未运行' }

# ---------- 引擎 ----------
Write-Step '引擎 DemoServer (8061)'
$java = Get-Process java -ErrorAction SilentlyContinue
if ($java) {
    # 只杀本项目的引擎；其它 java 进程（IDE、其它服务）不动
    $targets = $java | Where-Object { $_.Path -like '*\java.exe' }
    foreach ($t in $targets) {
        try {
            $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($t.Id)").CommandLine
            if ($cmd -like "*$EngineJarName*") { Stop-Process -Id $t.Id -Force; Write-Ok "已停止引擎 PID=$($t.Id)" }
        } catch { }
    }
    $left = Get-Process java -ErrorAction SilentlyContinue
    if ($left) { Write-Warn2 "还有 $($left.Count) 个 java 进程在跑（不是本项目引擎，未处理）" }
} else { Write-Ok '引擎未运行' }

# ---------- 授权服务 ----------
Write-Step '授权服务 grant-dev (8080)'
$grant = Get-Process grant-dev -ErrorAction SilentlyContinue
if ($grant) { $grant | Stop-Process -Force; Write-Ok '已停止' } else { Write-Ok '未运行' }

# ---------- Redis（可选） ----------
if ($IncludeRedis) {
    Write-Step 'Redis (6379)'
    $redis = Get-Process redis-server -ErrorAction SilentlyContinue
    if ($redis) { $redis | Stop-Process -Force; Write-Ok '已停止' } else { Write-Ok '未运行' }
} else {
    Write-Host "`n（Redis 与 MySQL 保留运行；要停 Redis 加 -IncludeRedis）" -ForegroundColor Gray
}

Write-Host ""
