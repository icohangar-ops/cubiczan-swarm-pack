$ErrorActionPreference = "Stop"

$missing = $false
$commands = @("rustc", "solana", "anchor", "surfpool", "node", "yarn")

foreach ($cmd in $commands) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        $version = & $cmd --version 2>&1 | Select-Object -First 1
        "{0,-8} {1}" -f $cmd, $version
    } else {
        "{0,-8} missing" -f $cmd
        $missing = $true
    }
}

if (Get-Command solana -ErrorAction SilentlyContinue) {
    ""
    solana config get
}

if ($missing) {
    ""
    "Install the Solana Developer Platform CLI from https://solana.com/docs/intro/installation"
    exit 1
}
