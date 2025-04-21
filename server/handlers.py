def register_handlers(mcp):
    @mcp.resource("list://respurces")
    def lsit_resources():
        """Lists all the available resources for this server"""

        return {
            "resources":[
                {
                    "uri" : "postgres://structure",
                    "name" : "postgres structure",
                    "description" : "Structure of postgres database",
                    "mime_type" : "text/plain"
                }
            ] 
        }
    
    @mcp.resource("postgres://structure")
    def postgres_structure():
        """Returns the structure of the postgres structure"""
        f = open("structure.txt")
        structure = f.read()
        return structure
