package transaction

import (
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

func genFilePath(dir string, tableName string, date time.Time) string {
	// file name format: {tableName}_{yyyy-mm-dd}.csv
	fileName := fmt.Sprintf("%s_%s.csv", tableName, date.Format(time.DateOnly))
	return path.Join(dir, fileName)
}

func findTableFile(dir string, tableName string) (string, error) {
	// 1. 获取dir下所有的csv文件
	files, err := os.ReadDir(dir)
	if err != nil {
		return "", err
	}

	// 2. 通过正则表达式解析{tableName}_yyyy-mm-dd.csv的文件列表
	pattern := fmt.Sprintf(`^%s_(\d{4}-\d{2}-\d{2})\.csv$`, regexp.QuoteMeta(tableName))
	re := regexp.MustCompile(pattern)

	type fileInfo struct {
		path string
		date time.Time
	}
	var matchedFiles []fileInfo

	for _, file := range files {
		if file.IsDir() {
			continue
		}
		if !strings.HasSuffix(strings.ToLower(file.Name()), ".csv") {
			continue
		}

		matches := re.FindStringSubmatch(file.Name())
		if len(matches) != 2 {
			continue
		}

		date, err := time.Parse(time.DateOnly, matches[1])
		if err != nil {
			continue
		}

		matchedFiles = append(matchedFiles, fileInfo{
			path: path.Join(dir, file.Name()),
			date: date,
		})
	}

	if len(matchedFiles) == 0 {
		return "", fmt.Errorf("no file found for table %s in %s", tableName, dir)
	}

	// 3. 在过滤的文件列表中, 获取最新的文件
	sort.Slice(matchedFiles, func(i, j int) bool {
		return matchedFiles[i].date.After(matchedFiles[j].date)
	})

	return matchedFiles[0].path, nil
}

func findAndCopyTableFile(dir string, tableName string) (string, error) {
	filePath, err := findTableFile(dir, tableName)
	if err != nil {
		return "", err
	}
	// filePath is {tableName}_{date}.csv
	fileName := filepath.Base(filePath)
	parts := strings.Split(fileName, "_")
	if len(parts) < 2 {
		return "", fmt.Errorf("invalid file name format: %s", fileName)
	}
	dateStr := strings.TrimSuffix(parts[len(parts)-1], ".csv")

	today := time.Now().Format(time.DateOnly)
	if dateStr != today {
		newFilePath := genFilePath(dir, tableName, time.Now())
		// 复制文件
		srcFile, err := os.Open(filePath)
		if err != nil {
			return "", err
		}
		defer srcFile.Close()

		dstFile, err := os.Create(newFilePath)
		if err != nil {
			return "", err
		}
		defer dstFile.Close()

		_, err = io.Copy(dstFile, srcFile)
		if err != nil {
			return "", err
		}
		return newFilePath, nil
	}
	return filePath, nil
}
