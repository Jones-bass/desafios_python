from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import Column, create_engine, inspect, Integer, String, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    address = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, fullname={self.fullname})"

class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    email_address = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)

    user = relationship("User", back_populates="address")

    def __repr__(self):
        return f"Address(id={self.id}, email_address={self.email_address})"

class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cpf = Column(String(11), nullable=False, unique=True)
    address = Column(String, nullable=False)

    accounts = relationship("Account", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Client(id={self.id}, name={self.name}, cpf={self.cpf}, address={self.address})"

class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    account_type = Column(String, nullable=False)
    agency = Column(String, nullable=False)
    number = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)

    client = relationship("Client", back_populates="accounts")

    def __repr__(self):
        return f"Account(id={self.id}, account_type={self.account_type}, agency={self.agency}, number={self.number})"

print(User.__tablename__)
print(Address.__tablename__)
print(Client.__tablename__)
print(Account.__tablename__)

# conexão com o banco de dados

database_path = 'D:\Search\desafios_python\integration_python_database\integrationWithSQL/databaseSQL.db'
engine = create_engine(f'sqlite:///{database_path}')

# criando as classes como tabelas no banco de dados
Base.metadata.create_all(engine)

# investiga o esquema de banco de dados
inspetor_engine = inspect(engine)
print(inspetor_engine.has_table("client"))
print(inspetor_engine.has_table("account"))
print(inspetor_engine.get_table_names())
print(inspetor_engine.default_schema_name)

with Session(engine) as session:
    jones = User(
        name='jones',
        fullname='Jones Souza',
        address=[Address(email_address='jonesbass.tb@gmail.com')]
    )

    sandy = User(
        name='sandy',
        fullname='Sandy Cardoso',
        address=[Address(email_address='sandy.tb@gemail.br'),
                 Address(email_address='sandysilva.tb@gmail.org')]
    )

    patrick = User(name='patrick', fullname='Patrick Cardoso')

    session.add_all([jones, sandy, patrick])

    # Criando instâncias de Client e Account
    client1 = Client(
        name='Carlos Silva',
        cpf='12345678901',
        address='Rua A, 123',
        accounts=[
            Account(account_type='corrente', agency='0001', number='123456'),
            Account(account_type='poupança', agency='0001', number='654321')
        ]
    )

    client2 = Client(
        name='Ana Paula',
        cpf='98765432100',
        address='Rua B, 456',
        accounts=[
            Account(account_type='corrente', agency='0002', number='112233')
        ]
    )

    session.add_all([client1, client2])
    session.commit()


# encerrando de fato a session
session.close()
