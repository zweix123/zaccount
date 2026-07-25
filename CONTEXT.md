# Personal Ledger

This context describes a private ledger that records and analyses changes in one person's funds.

## Language

**Ledger entry**:
A dated change in funds recorded against one account, with one type, a category path, optional tags, and an optional description.
_Avoid_: Transaction, record, item

**Account**:
A named place whose balance is affected by ledger entries, such as a bank account or payment wallet.
_Avoid_: Source

**Type**:
The fundamental direction and meaning of a ledger entry: income, expense, transfer in, or transfer out.
_Avoid_: Category, kind

**Category path**:
An ordered path through the fixed category tree belonging to a type. A prefix path is valid even when it does not end at a leaf.
_Avoid_: Category list, classification

**Tag**:
An independent, reusable label that connects ledger entries across the fixed category tree.
_Avoid_: Category

**Description**:
Free text that identifies or explains a ledger entry without carrying fixed classification semantics.
_Avoid_: Tag, memo category

**Transfer**:
One movement of funds between two accounts, represented by a matched transfer-out ledger entry and transfer-in ledger entry of equal amount and date.
_Avoid_: Two unrelated entries

**Ledger**:
The chronologically ordered collection of all ledger entries.
_Avoid_: Report, CSV
