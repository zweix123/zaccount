package transaction

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
	"time"

	ctg "github.com/zweix123/zaccount/backend/internal/domain/ctg"
)

func updateTable(filePath string) error {
	file, err := os.Create(filePath)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write(Fields)
	for _, row := range globalTransactionTable.data {
		writer.Write(marshalRow(row))
	}
	return nil
}

func readTable(filePath string) ([]*Transaction, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	transactions := make([]*Transaction, 0) // 初始化为空切片，而不是 nil
	lineNum := 0

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("failed to read CSV at line %d: %w", lineNum+1, err)
		}

		lineNum++

		// 跳过表头（第一行）
		if lineNum == 1 {
			continue
		}

		transaction, err := unmarshalRow(record)
		if err != nil {
			return nil, fmt.Errorf("failed to parse row at line %d: %w", lineNum, err)
		}
		transactions = append(transactions, transaction)
	}
	return transactions, nil
}

func marshalRow(transaction *Transaction) []string {
	return []string{
		transaction.Date.Format(time.DateOnly),
		string(transaction.Type),
		strconv.FormatFloat(transaction.Amount, 'f', -1, 64),
		strings.Join(transaction.Categorys, ","),
		strings.Join(transaction.Tags, ","),
		transaction.Desc,
	}
}

func unmarshalRow(record []string) (*Transaction, error) {
	if len(record) < 6 {
		return nil, fmt.Errorf("invalid record: expected 6 fields, got %d", len(record))
	}

	// 解析日期
	date, err := time.Parse(time.DateOnly, strings.TrimSpace(record[0]))
	if err != nil {
		return nil, fmt.Errorf("invalid date: %w", err)
	}

	// 解析类型
	typeStr := strings.TrimSpace(record[1])
	transactionType := TransactionType(typeStr)
	if !IsValidTransactionType(transactionType) {
		return nil, fmt.Errorf("invalid transaction type: %s, expected one of: 收入, 支出, 转入, 转出", typeStr)
	}

	// 解析金额
	amount, err := strconv.ParseFloat(strings.TrimSpace(record[2]), 64)
	if err != nil {
		return nil, fmt.Errorf("invalid amount: %w", err)
	}

	// 解析类别（逗号分隔）
	categoryStr := strings.TrimSpace(record[3])
	var category []string
	if categoryStr != "" {
		category = strings.Split(categoryStr, ",")
		for j := range category {
			category[j] = strings.TrimSpace(category[j])
		}
	}
	if isValid := ctg.GetInstance().IsValid(string(transactionType), category); !isValid {
		return nil, fmt.Errorf("invalid category: %s for transaction type: %s", categoryStr, transactionType)
	}

	// 解析标签（逗号分隔）
	tagsStr := strings.TrimSpace(record[4])
	var tags []string
	if tagsStr != "" {
		tags = strings.Split(tagsStr, ",")
		for j := range tags {
			tags[j] = strings.TrimSpace(tags[j])
		}
	}

	// 解析描述
	desc := strings.TrimSpace(record[5])

	return &Transaction{
		Date:      date,
		Type:      transactionType,
		Amount:    amount,
		Categorys: category,
		Tags:      tags,
		Desc:      desc,
	}, nil
}
