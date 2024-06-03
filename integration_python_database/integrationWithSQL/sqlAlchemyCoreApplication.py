from sqlalchemy import create_engine, text, ForeignKey, MetaData, Table, Column, Integer, String

# Database path
database_path = 'D:/Python/integration_python_database/integrationWithSQL/database.db'
engine = create_engine(f'sqlite:///{database_path}')

# Metadata and table definitions
metadata_obj = MetaData()

# Define user table
user = Table(
    'user',
    metadata_obj,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', String(40), nullable=False),
    Column('email_address', String(60)),
    Column('nickname', String(50), nullable=False),
)

# Define user_prefs table
user_prefs = Table(
    'user_prefs', metadata_obj,
    Column('pref_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey("user.user_id"), nullable=False),
    Column('pref_name', String(40), nullable=False),
    Column('pref_value', String(100))
)

# Print table information for verification
print("\nInfo da tabela user_prefs")
print(user_prefs.primary_key)
print(user_prefs.constraints)

print(metadata_obj.tables)

for table in metadata_obj.sorted_tables:
    print(table)

# Create all tables
metadata_obj.create_all(engine)

# Define financial_info table
metadata_bd_obj = MetaData()
financial_info = Table(
    'financial_info',
    metadata_bd_obj,
    Column('id', Integer, primary_key=True),
    Column('value', String(100), nullable=False),
)

# Create financial_info table
metadata_bd_obj.create_all(engine)

# Insert info into the user table
insert_statements = [
    text("insert into user values(1, 'Jones', 'jonesbass.tb@gmail.com', 'Jhon')"),
    text("insert into user values(2, 'Maria', 'maria@example.com', 'Ma')"),
    text("insert into user values(3, 'Alice', 'alice@example.com', 'Ally')"),
]

# Execute the SQL insert statements
with engine.connect() as connection:
    for stmt in insert_statements:
        connection.execute(stmt)

# Print financial_info table information for verification
print("\nInfo da tabela financial_info")
print(financial_info.primary_key)
print(financial_info.constraints)

# Execute and print the result of the select statement
print('\nExecutando statement SQL')
sql = text('select * from user')

with engine.connect() as connection:
    result = connection.execute(sql)
    for row in result:
        print(row)
