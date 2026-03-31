from expense_tracker import crud,database,schemas
from datetime import date

db=next(database.get_db())
new_expense = schemas.ExpenseCreate(description='new expense test', amount=50,date=date(2022,5,5))

result = crud.create_expense(db,new_expense)
print(result.id, result.description)

delete_expense = crud.delete_expense(db, expense_id=21)
if delete_expense:
    print("succeddully deleted")
else:
    print("Unsuccessful attempt to delete")

yearly = crud.yearly_total(db, year=2022)
print(yearly)