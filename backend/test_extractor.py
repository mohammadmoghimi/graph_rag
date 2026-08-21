from knowledge.extractor import extract_graph_data


text = """
دانشگاه تهران یکی از قدیمی‌ترین دانشگاه‌های ایران است.
این دانشگاه در شهر تهران قرار دارد.
"""


result = extract_graph_data(text)

print(result)