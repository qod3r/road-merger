from pypdf import PdfMerger
import os, sys
from pprint import pprint


merger = PdfMerger()

street = sys.argv[1]
dirs = []
for dir in os.listdir():
	if street in dir.lower() and os.path.isdir(dir):
		dirs.append(dir)
print("Найдены улицы:")
print(*[f"\t{dir}" for dir in dirs], sep="\n")
print("Начать слияние? (д/н)")
ans = input()
if 'д' not in ans:
	print("отменено")
	exit(0)
print("работаем...")

order = ['паспорт', 'разметка', 'лг']
order2 = [*[f'п{n}' for n in range(1,9)], *[f'о{n}' for n in range(1,9)]]

flag = False
for dir in dirs:
	pdf_list = []
	os.chdir(dir)
	for file in os.listdir():
		if '.pdf' in file:
			pdf_list.append(file)
	pdf_list = sorted(pdf_list)

	for tag in order:
		print(f"{dir}: {tag} ... ", end="", flush=True)
		for pdf in pdf_list:
			if tag in pdf:
				merger.append(pdf)
				flag = True
				print("OK")
		if not flag:
			print("X")
		flag = False
	os.chdir('..')
for dir in dirs:
	os.chdir(dir)
	for tag in order2:
		for pdf in pdf_list:
			if tag in pdf:
				merger.append(pdf)
				print(f"{tag} ", end="", flush=True)
	os.chdir('..')
	

#orig_name = f"Техпаспорт ул. {'_'.join(os.getcwd().split('_')[-2:])}.pdf"
name = '_'.join(dirs[0].split('_')[-2:]).strip('\\')
orig_name = f"Техпаспорт ул. {name}.pdf"
merger.write(orig_name)
print("ОК")
merger.close()