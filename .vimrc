" ===============================================================================
" Vimrc - Abhinaba Basu http://www.bonggeek.com
" ===============================================================================

" Show fancy colors =============================================================
syn on                              " Syntax highlighting on
colorscheme desert " choose a darker color scheme

if has("gui_running")
  if has("gui_gtk2") || has("gui_gtk3")
    set guifont=Courier\ New\ 11
  elseif has("gui_photon")
    set guifont=Courier\ New:s11
  elseif has("gui_kde")
    set guifont=Courier\ New/11/-1/5/50/0/0/0/1/0
  elseif has("x11")
    set guifont=-*-courier-medium-r-normal-*-*-180-*-*-m-*-*
  else
    set guifont=Courier_New:h11:cDEFAULT
  endif
endif

set vb t_vb=
set belloff=all

set ls=2                            " allways show status line
set number                          " show line numbers
set nowrap                          " Don't wrap lines
set ruler                           " show line and column
set showmatch                       " show matching braces

" Tab and indent options  =======================================================
set tabstop=4                       " Tab is 4 spaces and NOT the default 8
set shiftwidth=4                    " numbers of spaces to (auto)indent
set expandtab                       " Expand tab to spaces
set cindent                         " cindent
set smartindent                     " smart indent
set autoindent                      " always set autoindenting on
set softtabstop=4                   " makes the spaces feel like real tabs. E.g. back deletes all 4 chars
set backspace=indent,eol,start      " backspace deletes indent, eol and start line

" Search options  ===============================================================
set smartcase                       " Ignore spaces in seach (I use Windows!!!!)
set incsearch                       " do incremental searching
set hlsearch                        " highlight searches

" File options  =================================================================
set nobackup                        " do not keep a backup file. I hate '~' in file names
map <C-s> :w <cr>
nmap <F11> :silent !start explorer /select,%:p <cr> " open and select in explorer

"Razzle build commands ==========================================================
autocmd BufEnter * lcd %:p:h        " on file open cd to it's folder
map <f6>  :!build %:p:h <cr>        " F6 builds
map <C-f6>  :!build -c %:p:h <cr>   " Ctrl+F6 clean builds
map <c-t> :silent !tf edit % <cr>   " Ctrl+t checks out file (tf -edit)
map <c-d> :silent !tf diff % <cr>   " ctrl+d does a tf -diff of the current file

execute pathogen#infect()
filetype plugin indent on
set rtp+=$GOPATH/src/github.com/golang/lint/misc/vim
