from knowledge.graph import get_driver


driver = get_driver()

try:
    driver.verify_connectivity()
    print("Neo4j connection successful")
finally:
    driver.close()