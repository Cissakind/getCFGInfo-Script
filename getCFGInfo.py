import os
import sys
import json
import time
import csv
import subprocess

def compile(fileDir, filename , opt):
	compile_gen = "clang -g -fno-omit-frame-pointer -fno-inline -ggdb " + opt + " -std=c11 -Wall -fno-stack-protector -no-pie -o " + fileDir[:-2] + ".d/" + filename + opt + " " + fileDir
	compile_proc = subprocess.run(compile_gen.split(" "), stderr=subprocess.PIPE)

def run_map(fileDir, filename, opt):
	run_map = ['cfggrind_asmmap', fileDir[:-2] + ".d/" + filename + opt]
	with open(fileDir[:-2] + ".d/" + filename + opt + '.map', "w") as outfile:
		subprocess.run(run_map, stdout=outfile)

def run_bench(fileDir, filename, opt, switch_num, k, funcName):
	
	run_valgrind = 'valgrind --tool=cfggrind --cfg-outfile=' + fileDir[:-2] + ".d/" + filename + '_' + k + '_' + opt[1:] + '.cfg --instrs-map=' + fileDir[:-2] + ".d/" + filename + opt + '.map ' + fileDir[:-2] + ".d/" + filename + opt + ' ' + switch_num
	subprocess.run(run_valgrind.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	run_cfggrind = ['cfggrind_info', '-f', filename + opt + "::" + funcName.strip() , '-s', 'functions', '-m', 'json', fileDir[:-2] + ".d/" + filename + '_' + k + '_' + opt[1:] + '.cfg']
	print(run_cfggrind)
	with open(fileDir[:-2] + ".d/" + filename + '_' + k + '_' + opt  + '.info', "w") as outfile:
		subprocess.run(run_cfggrind, stdout=outfile)


def main():
	all_bench_dir = './small_jotai'

	time_dict = {}
	optLevelList = ['-O0', '-O1', '-O2', '-O3', '-Oz', '-Os', 'Ofast']
	ketList = ['int-bounds','big-arr','big-arr-10x','linked','dlinked','bintree']
	for opt in optLevelList:
		time_dict[opt] = []

	name_and_constraint_file = open('smallconstraint_number_anghaLeaves.csv', 'r')
	lines = name_and_constraint_file.readlines()
	toConstraint = {}
	for line in lines:
		filename,int_bounds,big_arr,big_arr_10x,linked,dlinked,bintree = line.split(',')
		if bintree == '\n':
			bintree = ''
		toConstraint[filename] = [int_bounds,big_arr,big_arr_10x,linked,dlinked,bintree]
		print(toConstraint[filename])
		

	name_and_case_file = open('smallfiletofunc.csv', 'r')
	lines = name_and_case_file.readlines()
	for line in lines:
		benchmark_name, func_name = line.split(',')
		constraintList = toConstraint[benchmark_name]
		benchmark_name = benchmark_name[:-2] + '_Final.c'
		fileDir = all_bench_dir + '/' + benchmark_name
		
		if not os.path.isdir(fileDir[:-2] + ".d"):
			os.mkdir(fileDir[:-2] + ".d")

		for opt in optLevelList:
			compile(fileDir, benchmark_name, opt)
			run_map(fileDir, benchmark_name, opt)
			for idx in range(len(constraintList)): 
				if constraintList[idx]:
					run_bench(fileDir, benchmark_name, opt, constraintList[idx], ketList[idx], func_name)



if __name__ == '__main__':
	main()