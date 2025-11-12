package category

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/zweix123/zaccount/backend/common/logger"
)

func setup() {
	logger.InitLogger("debug")
}
func teardown() {}
func TestMain(m *testing.M) {
	setup()         // 全局初始化
	code := m.Run() // testing.M的唯一方法，执行所在包下的所有TestXxx函数
	teardown()      // 全局清理
	os.Exit(code)
}

func TestCtg_Contains(t *testing.T) {
	ctg := GetInstance()
	assert.True(t, ctg.IsValid("收入", []string{"工资"}))
	assert.True(t, ctg.IsValid("支出", []string{"餐饮", "午饭"}))
	assert.False(t, ctg.IsValid("支出", []string{"餐饮", "早餐"}))
}
