package transaction

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestGenFilePath(t *testing.T) {
	testCases := []struct {
		name      string
		dir       string
		tableName string
		date      time.Time
		want      string
	}{
		{
			name:      "正常情况",
			dir:       "test_dir",
			tableName: "test_table",
			date:      time.Date(2021, 1, 1, 0, 0, 0, 0, time.UTC),
			want:      "test_dir/test_table_2021-01-01.csv",
		},
		{
			name:      "不同日期",
			dir:       "data",
			tableName: "transaction",
			date:      time.Date(2025, 12, 31, 0, 0, 0, 0, time.UTC),
			want:      "data/transaction_2025-12-31.csv",
		},
		{
			name:      "空目录",
			dir:       "",
			tableName: "test",
			date:      time.Date(2023, 6, 15, 0, 0, 0, 0, time.UTC),
			want:      "test_2023-06-15.csv",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			filePath := genFilePath(tc.dir, tc.tableName, tc.date)
			assert.Equal(t, tc.want, filePath)
		})
	}
}

func TestFindTableFile(t *testing.T) {
	testCases := []struct {
		name        string
		setup       func(t *testing.T) (string, func()) // 返回目录路径和清理函数
		tableName   string
		wantErr     bool
		errContains string
		validate    func(t *testing.T, filePath string)
	}{
		{
			name: "正常情况-多个匹配文件",
			setup: func(t *testing.T) (string, func()) {
				tmpDir, err := os.MkdirTemp("", "test_find_table_*")
				assert.NoError(t, err)
				files := []string{
					"transaction_2025-01-01.csv",
					"transaction_2025-01-15.csv",
					"transaction_2025-02-01.csv",
				}
				for _, fileName := range files {
					err := os.WriteFile(filepath.Join(tmpDir, fileName), []byte("test"), 0o644)
					assert.NoError(t, err)
				}
				return tmpDir, func() { os.RemoveAll(tmpDir) }
			},
			tableName: "transaction",
			wantErr:   false,
			validate: func(t *testing.T, filePath string) {
				assert.Contains(t, filePath, "2025-02-01")
			},
		},
		{
			name: "无匹配文件-空目录",
			setup: func(t *testing.T) (string, func()) {
				tmpDir, err := os.MkdirTemp("", "test_empty_*")
				assert.NoError(t, err)
				return tmpDir, func() { os.RemoveAll(tmpDir) }
			},
			tableName:   "transaction",
			wantErr:     true,
			errContains: "no file found",
			validate: func(t *testing.T, filePath string) {
				assert.Empty(t, filePath)
			},
		},
		{
			name: "目录不存在",
			setup: func(t *testing.T) (string, func()) {
				nonExistentDir := filepath.Join(os.TempDir(), "nonexistent_dir_12345")
				return nonExistentDir, func() {}
			},
			tableName: "transaction",
			wantErr:   true,
			validate: func(t *testing.T, filePath string) {
				assert.Empty(t, filePath)
			},
		},
		{
			name: "只有不匹配的文件",
			setup: func(t *testing.T) (string, func()) {
				tmpDir, err := os.MkdirTemp("", "test_nonmatching_*")
				assert.NoError(t, err)
				files := map[string][]byte{
					"other_table_2025-01-01.csv": []byte("test"),
					"transaction.txt":            []byte("test"),
					"not_a_csv":                  []byte("test"),
					"transaction_2025-13-01.csv": []byte("test"), // 无效日期
				}
				for fileName, content := range files {
					err := os.WriteFile(filepath.Join(tmpDir, fileName), content, 0o644)
					assert.NoError(t, err)
				}
				return tmpDir, func() { os.RemoveAll(tmpDir) }
			},
			tableName:   "transaction",
			wantErr:     true,
			errContains: "no file found",
			validate: func(t *testing.T, filePath string) {
				assert.Empty(t, filePath)
			},
		},
		{
			name: "多个文件返回最新的",
			setup: func(t *testing.T) (string, func()) {
				tmpDir, err := os.MkdirTemp("", "test_multiple_*")
				assert.NoError(t, err)
				files := []struct {
					name string
					date string
				}{
					{"transaction_2024-12-01.csv", "2024-12-01"},
					{"transaction_2025-03-15.csv", "2025-03-15"},
					{"transaction_2025-01-10.csv", "2025-01-10"},
				}
				for _, f := range files {
					err := os.WriteFile(filepath.Join(tmpDir, f.name), []byte("test"), 0o644)
					assert.NoError(t, err)
				}
				return tmpDir, func() { os.RemoveAll(tmpDir) }
			},
			tableName: "transaction",
			wantErr:   false,
			validate: func(t *testing.T, filePath string) {
				assert.Contains(t, filePath, "2025-03-15")
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			dir, cleanup := tc.setup(t)
			defer cleanup()

			filePath, err := findTableFile(dir, tc.tableName)

			if tc.wantErr {
				assert.Error(t, err)
				if tc.errContains != "" {
					assert.Contains(t, err.Error(), tc.errContains)
				}
			} else {
				assert.NoError(t, err)
				assert.Contains(t, filePath, dir)
			}

			if tc.validate != nil {
				tc.validate(t, filePath)
			}
		})
	}
}

func TestFindAndCopyTableFile(t *testing.T) {
	testCases := []struct {
		name      string
		setup     func(t *testing.T) (string, []byte, func()) // 返回目录路径、原始内容和清理函数
		tableName string
		wantErr   bool
		validate  func(t *testing.T, filePath string, originalContent []byte)
	}{
		{
			name: "正常情况-复制旧文件到新日期",
			setup: func(t *testing.T) (string, []byte, func()) {
				tmpDir, err := os.MkdirTemp("", "test_copy_table_*")
				assert.NoError(t, err)
				// 创建一个旧日期的文件（昨天的）
				yesterday := time.Now().AddDate(0, 0, -1)
				oldFileName := fmt.Sprintf("transaction_%s.csv", yesterday.Format(time.DateOnly))
				oldFilePath := filepath.Join(tmpDir, oldFileName)
				testContent := []byte("date,type,amount\n2025-01-01,转入,1000.00")
				err = os.WriteFile(oldFilePath, testContent, 0o644)
				assert.NoError(t, err)
				return tmpDir, testContent, func() { os.RemoveAll(tmpDir) }
			},
			tableName: "transaction",
			wantErr:   false,
			validate: func(t *testing.T, filePath string, originalContent []byte) {
				// 验证返回的文件路径是今天的日期
				today := time.Now().Format(time.DateOnly)
				assert.Contains(t, filePath, today)
				// 验证新文件存在
				_, err := os.Stat(filePath)
				assert.NoError(t, err)
				// 验证新文件内容与原文件一致
				newFileContent, err := os.ReadFile(filePath)
				assert.NoError(t, err)
				assert.Equal(t, originalContent, newFileContent)
			},
		},
		{
			name: "文件已经是今天的日期-不复制",
			setup: func(t *testing.T) (string, []byte, func()) {
				tmpDir, err := os.MkdirTemp("", "test_copy_table_today_*")
				assert.NoError(t, err)
				// 创建今天日期的文件
				today := time.Now().Format(time.DateOnly)
				todayFileName := fmt.Sprintf("transaction_%s.csv", today)
				todayFilePath := filepath.Join(tmpDir, todayFileName)
				testContent := []byte("date,type,amount\n2025-01-01,转入,1000.00")
				err = os.WriteFile(todayFilePath, testContent, 0o644)
				assert.NoError(t, err)
				return tmpDir, testContent, func() { os.RemoveAll(tmpDir) }
			},
			tableName: "transaction",
			wantErr:   false,
			validate: func(t *testing.T, filePath string, originalContent []byte) {
				// 验证返回的文件路径是今天的日期
				today := time.Now().Format(time.DateOnly)
				assert.Contains(t, filePath, today)
				// 验证文件存在
				_, err := os.Stat(filePath)
				assert.NoError(t, err)
			},
		},
		{
			name: "找不到文件-返回错误",
			setup: func(t *testing.T) (string, []byte, func()) {
				tmpDir, err := os.MkdirTemp("", "test_copy_table_empty_*")
				assert.NoError(t, err)
				return tmpDir, nil, func() { os.RemoveAll(tmpDir) }
			},
			tableName: "transaction",
			wantErr:   true,
			validate: func(t *testing.T, filePath string, originalContent []byte) {
				assert.Empty(t, filePath)
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			dir, originalContent, cleanup := tc.setup(t)
			defer cleanup()

			filePath, err := findAndCopyTableFile(dir, tc.tableName)

			if tc.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.Contains(t, filePath, dir)
			}

			if tc.validate != nil {
				tc.validate(t, filePath, originalContent)
			}
		})
	}
}
