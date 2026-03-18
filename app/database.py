from sqlmodel import create_engine, Session

sqlite_file_name = "barbershop.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Echo true has to be removed
engine = create_engine(sqlite_url, echo=True)

'''
get_session() creates a database session. 
Using the with statement is the best decision 
because it automatically closes the connection 
once the process is finished
'''

def get_session():
    with Session(engine) as session:
        yield session