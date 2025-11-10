package category

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"sync"

	"github.com/zweix123/zaccount/backend/common/util"
)

type Ctg struct {
	data interface{}
}

var (
	instance *Ctg
	once     sync.Once
)

func GetInstance() *Ctg {
	once.Do(func() {
		instance = &Ctg{}
		instance.init(util.GetRalePath("..", "..", "..", "..", "config", "ctg.jsonc"))
	})
	return instance
}

func (c *Ctg) init(ctgPath string) {
	fmt.Println("load ctg from: ", ctgPath)
	data, err := os.ReadFile(ctgPath)
	if err != nil {
		panic(fmt.Errorf("failed to read file: %w", err))
	}
	data = removeJSONCComments(data)
	err = json.Unmarshal(data, &c.data)
	if err != nil {
		panic(fmt.Errorf("failed to unmarshal file: %w", err))
	}
	fmt.Println("load ctg success")
}

func removeJSONCComments(data []byte) []byte {
	// 移除多行注释 (/* ... */)
	multiLinePattern := `/\*[^*]*\*+([^/*][^*]*\*+)*/`
	re := regexp.MustCompile(multiLinePattern)
	data = re.ReplaceAll(data, nil)

	// 移除单行注释 (// ...)
	singleLinePattern := `//[^\n]*\n?`
	re = regexp.MustCompile(singleLinePattern)
	data = re.ReplaceAll(data, []byte("\n"))

	return data
}

func mapInterfaceContains(data interface{}, ctg string) (interface{}, bool) {
	dataMap, ok := data.(map[string]interface{})
	if !ok { // 代码 bug or 到 leaf node 了
		return nil, false
	}
	for k, v := range dataMap {
		if k == ctg {
			return v, true
		}
	}
	return nil, false
}

func (c *Ctg) IsValid(categoryType string, categorys []string) bool {
	curData, curRes := mapInterfaceContains(c.data, categoryType)
	if !curRes {
		return false
	}
	for _, category := range categorys {
		curData, curRes = mapInterfaceContains(curData, category)
		if !curRes {
			return false
		}
	}
	return true
}
