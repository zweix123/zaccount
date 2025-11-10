package util

import (
	"path/filepath"
	"runtime"

	"github.com/zweix123/suger/common"
)

func genRalePath(dir string, path ...string) string {
	for _, p := range path {
		if p == "" || p == "." {
			continue
		}
		if p == ".." {
			dir = filepath.Dir(dir)
			continue
		}
		dir = filepath.Join(dir, p)
	}
	return dir
}

func GetRalePath(path ...string) string {
	_, file, _, ok := runtime.Caller(1)
	common.Assert(ok, "failed to get caller")
	return genRalePath(filepath.Dir(file), path...)
}
