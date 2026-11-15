<#
    校园文创产品生产管理系统 —— 一键启动脚本
    按课程要求的环境顺序启动：MySQL -> Redis -> 授权服务(grant) -> 引擎(8061) -> nginx(30666)

    用法：
        .\start-all.ps1              # 启动全部（已在运行的会跳过）
        .\start-all.ps1 -Build       # 先 mvn package 再启动
        .\start-all.ps1 -SkipNginx   # 不用前端，只起后端

    若提示"禁止运行脚本"，先执行：
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>
[CmdletBinding()]
param(
    [switch]$Build,
    [switch]$SkipNginx
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$logDir = Join-Path $root '.runtime\logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# ============ 路径配置（换电脑只改这一段） ============
$JavaHome   = 'D:\Java\JDK1.8'
$MavenHome  = 'E:\maven\apache-maven-3.9.1'
$MavenRepo  = 'D:\maven\repository'
$RedisExe   = 'E:\redis\redis-server.exe'
$GrantExe   = Join-Path $root 'sie-grant\grant-dev.exe'
$BackendDir = Join-Path $root 'iidp-backend-demo'
$EngineJar  = Join-Path $BackendDir 'sie-iidp-demo-start\target\sie-iidp-demo-start-1.0-SNAPSHOT.jar'
$NginxDir   = Join-Path $root '.runtime\nginx-windows\nginx-1.30.6-windows'
$NginxExe   = Join-Path $NginxDir 'nginx.exe'
$AppUrl     = 'http://localhost:30666/iidp/'
# ======================================================

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    OK  $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "    !!  $msg" -ForegroundColor Yellow }

function Test-Port([int]$port) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', $port); $c.Close(); return $true
    } catch { return $false }
}

function Wait-Port([int]$port, [int]$seconds, [string]$what) {
    for ($i = 0; $i -lt $seconds; $i++) {
        if (Test-Port $port) { return $true }
        Start-Sleep -Seconds 1
    }
    Write-Warn2 "$what 在 $seconds 秒内没有监听 $port"
    return $false
}

Write-Host "`n校园文创产品生产管理系统 · 启动`n" -ForegroundColor White

# ---------- 0. MySQL ----------
Write-Step '0/5 MySQL (3306)'
if (Test-Port 3306) { Write-Ok '已在运行' }
else {
    $svc = Get-Service -Name 'MySQL*' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($svc) {
        Start-Service $svc.Name
        if (Wait-Port 3306 30 'MySQL') { Write-Ok "服务 $($svc.Name) 已启动" }
    } else {
        Write-Warn2 '没找到 MySQL 服务，请手工启动（3306 必须可用）'
    }
}

# ---------- 1. Redis ----------
Write-Step '1/5 Redis (6379)'
if (Test-Port 6379) { Write-Ok '已在运行' }
else {
    if (-not (Test-Path $RedisExe)) { Write-Warn2 "找不到 $RedisExe" }
    else {
        Start-Process -FilePath $RedisExe -WorkingDirectory (Split-Path $RedisExe) -WindowStyle Minimized
        if (Wait-Port 6379 15 'Redis') { Write-Ok '已启动' }
    }
}

# ---------- 2. 授权服务 ----------
Write-Step '2/5 授权服务 grant-dev (8080)'
if (Test-Port 8080) { Write-Ok '已在运行' }
else {
    if (-not (Test-Path $GrantExe)) { Write-Warn2 "找不到 $GrantExe" }
    else {
        Start-Process -FilePath $GrantExe -WorkingDirectory (Split-Path $GrantExe) -WindowStyle Minimized `
            -RedirectStandardOutput (Join-Path $logDir 'grant-out.log') `
            -RedirectStandardError  (Join-Path $logDir 'grant-err.log')
        if (Wait-Port 8080 15 '授权服务') { Write-Ok '已启动' }
    }
}

# ---------- 3. 引擎 ----------
Write-Step '3/5 引擎 DemoServer (8061)'
if (Test-Port 8061) { Write-Ok '已在运行' }
else {
    if ($Build) {
        Write-Host '    先构建三个 APP（约 10-30 秒）...' -ForegroundColor Gray
        $env:JAVA_HOME = $JavaHome
        $env:PATH = "$JavaHome\bin;$env:PATH"
        $env:MAVEN_ARGS = "-Dmaven.repo.local=$MavenRepo"
        Push-Location $BackendDir
        try {
            & "$MavenHome\bin\mvn.cmd" -s settings.xml -o -q -DskipTests package
            if ($LASTEXITCODE -ne 0) { Write-Warn2 'mvn package 失败，构建产物可能不完整' }
            else { Write-Ok '构建完成，jar 已复制到 apps/modules' }
        } finally { Pop-Location }
    }
    if (-not (Test-Path $EngineJar)) { throw "找不到引擎 jar：$EngineJar（先执行一次 .\start-all.ps1 -Build）" }
    # 引擎按相对路径读 apps/ 与 apps/modules，工作目录必须是 iidp-backend-demo
    Start-Process -FilePath "$JavaHome\bin\java.exe" `
        -ArgumentList '-Dfile.encoding=UTF-8', '-jar', $EngineJar `
        -WorkingDirectory $BackendDir -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir 'engine-out.log') `
        -RedirectStandardError  (Join-Path $logDir 'engine-err.log')
    Write-Host '    等待引擎（正常 15-25 秒）...' -ForegroundColor Gray
    if (Wait-Port 8061 60 '引擎') {
        Write-Ok "已监听 8061，日志：$logDir\engine-out.log"
    } else {
        Write-Warn2 "引擎没起来，看 $logDir\engine-out.log 与 engine-err.log"
    }
}

# ---------- 4. nginx ----------
if (-not $SkipNginx) {
    Write-Step '4/5 nginx 前端 (30666)'
    if (Test-Port 30666) { Write-Ok '已在运行' }
    else {
        if (-not (Test-Path $NginxExe)) { Write-Warn2 "找不到 $NginxExe" }
        else {
            Start-Process -FilePath $NginxExe -WorkingDirectory $NginxDir -WindowStyle Hidden
            if (Wait-Port 30666 15 'nginx') { Write-Ok '已启动' }
        }
    }
}

# ---------- 汇总 ----------
Write-Host "`n端口状态" -ForegroundColor White
foreach ($p in @(3306, 6379, 8080, 8061, 30666)) {
    $on = Test-Port $p
    $name = @{ 3306 = 'MySQL'; 6379 = 'Redis'; 8080 = 'grant'; 8061 = 'engine'; 30666 = 'nginx' }[$p]
    $mark = if ($on) { '[up]  ' } else { '[down]' }
    $color = if ($on) { 'Green' } else { 'Red' }
    Write-Host ("  {0} {1,-6} {2}" -f $mark, $p, $name) -ForegroundColor $color
}

if ((Test-Port 30666) -and (Test-Port 8061)) {
    Write-Host "`n打开：$AppUrl" -ForegroundColor Green
    Write-Host "账号：admin_000001 / Admin_000001      平台租户管理员：implementer / Implementer_2023`n" -ForegroundColor Gray
} else {
    Write-Host "`n服务未起全，请按上面的 [down] 项排查。`n" -ForegroundColor Yellow
}
