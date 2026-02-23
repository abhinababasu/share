# ---------------------------
# Basic navigation / listing
# ---------------------------
Set-Alias d Get-ChildItem
Set-Alias l Get-ChildItem
Set-Alias c Clear-Host
Set-Alias t Get-Content

# "more" style paging
function m {
  param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
  if ($Args.Count -gt 0) {
    Get-Content @Args | Out-Host -Paging
  } else {
    $input | Out-Host -Paging
  }
}

# tree /f
function tr { tree /f @args }

# pushd/popd equivalents (PowerShell has Push-Location/Pop-Location)
function pu { Push-Location @args }
function po { Pop-Location }

# .. / .... / ...... (your CMD file has multi-dot pushd shortcuts)
function .. { Set-Location .. }
function .... { Set-Location ..\.. }
function ...... { Set-Location ..\..\.. }

# ---------------------------
# Git helpers
# ---------------------------
function gstat   { git status @args }
function gstats  { git status -s @args }
function gadd    { git add @args }
function gd      { git diff @args }
function gds     { git diff --staged @args }
function gvdiff  { git difftool --tool=gvimdiff -y @args }
function gdiff   { git difftool -y @args }
function commit  { git commit @args }
function commita { git commit -a @args }
function log     { git log @args }
function logp    { git log --date=iso "--pretty=format:%H %C(yellow)%ad %C(bold cyan)%ae %C(green)%s" @args }
function pull    { git pull @args }
function push    { git push @args }
function branch  { git branch @args }
function branches{ git log --oneline --decorate --graph --all @args }

# ---------------------------
# findstr equivalents (Select-String)
# ---------------------------
# Note: findstr /snip is approximated by Select-String output (file:line + matching line).
function fc {
  param([Parameter(Mandatory=$true)][string]$Pattern)
  Select-String -SimpleMatch -Pattern $Pattern -Path *.c,*.h,*.cpp,*.asm,*.src,*.hpp,*.inl,*.inc
}

function fh {
  param([Parameter(Mandatory=$true)][string]$Pattern)
  Select-String -SimpleMatch -Pattern $Pattern -Path *.h,*.hpp,*.inl,*.inc
}

function fcs {
  param([Parameter(Mandatory=$true)][string]$Pattern)
  Select-String -SimpleMatch -Pattern $Pattern -Path *.cs
}

# f = find in specific files you pass in (like findstr /c:pattern file1 file2 ...)
function f {
  param(
    [Parameter(Mandatory=$true)][string]$Pattern,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$Paths
  )
  if (-not $Paths -or $Paths.Count -eq 0) {
    throw "Usage: f <pattern> <file/glob> [more files/globs...]"
  }
  Select-String -SimpleMatch -Pattern $Pattern -Path $Paths
}

# ---------------------------
# Editors/tools
# ---------------------------
function g  { gvim @args }
function de { devenv @args }
function n  { notepad @args }

# ---------------------------
# Kubernetes
# ---------------------------
function k8 { kubectl @args }

# ---------------------------
# Repo jump shortcuts
# ---------------------------
function mass { Push-Location 'c:\git\MASS' }
function dts  { Push-Location 'c:\git\DTS' }