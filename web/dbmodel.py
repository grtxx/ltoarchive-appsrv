
import model.variables as variables
import model.tape
import model.archivedomain
import model.folder
import model.file
import model.file2tape


def createAll():
    variables.Declarative_Base.metadata.create_all( variables.DBEngine )

