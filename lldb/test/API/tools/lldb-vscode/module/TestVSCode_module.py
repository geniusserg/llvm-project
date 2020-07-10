"""
Test lldb-vscode setBreakpoints request
"""

from __future__ import print_function

import unittest2
import vscode
from lldbsuite.test.decorators import *
from lldbsuite.test.lldbtest import *
from lldbsuite.test import lldbutil
import lldbvscode_testcase


class TestVSCode_module(lldbvscode_testcase.VSCodeTestCaseBase):

    mydir = TestBase.compute_mydir(__file__)
    
    def test_modules_event(self):
        program_basename = "a.out.stripped"
        program= self.getBuildArtifact(program_basename)
        self.build_and_launch(program)
        functions = ['foo']
        breakpoint_ids = self.set_function_breakpoints(functions)
        self.assertEquals(len(breakpoint_ids), len(functions),
                        'expect one breakpoint')
        self.continue_to_breakpoints(breakpoint_ids)
        active_modules = self.vscode.get_active_modules()
        self.assertIn(program_basename, active_modules, '%s module is in active modules' % (program_basename))
        program_module = active_modules[program_basename]
        self.assertIn('name', program_module, 'make sure name is in module')
        self.assertEqual(program_basename, program_module['name'])
        self.assertIn('path', program_module, 'make sure path is in module')
        self.assertEqual(program, program_module['path'])
        self.assertTrue('symbolFilePath' not in program_module, 'Make sure a.out.stripped has no debug info')
        self.assertEqual('Symbols not found.', program_module['symbolStatus'])
        symbol_path = self.getBuildArtifact("a.out")
        self.vscode.request_evaluate('`%s' % ('target symbols add -s "%s" "%s"' % (program, symbol_path)))
        active_modules = self.vscode.get_active_modules()
        program_module = active_modules[program_basename]
        self.assertEqual(program_basename, program_module['name'])
        self.assertEqual(program, program_module['path'])
        self.assertEqual('Symbols loaded.', program_module['symbolStatus'])
        self.assertIn('symbolFilePath', program_module)
        self.assertEqual(symbol_path, program_module['symbolFilePath'])
        self.assertIn('addressRange', program_module)

    def test_compile_units(self):
        program= self.getBuildArtifact("a.out")
        self.build_and_launch(program)
        source = "main.cpp"
        main_source_path = self.getSourcePath(source)
        breakpoint1_line = line_number(source, '// breakpoint 1')
        lines = [breakpoint1_line]
        breakpoint_ids = self.set_source_breakpoints(source, lines)
        self.continue_to_breakpoints(breakpoint_ids)
        moduleId = self.vscode.get_active_modules()['a.out']['id']
        response = self.vscode.request_getCompileUnits(moduleId)
        print(response['body'])
        self.assertTrue(response['body'])
        self.assertTrue(len(response['body']['compileUnits']) == 1,
                        'Only one source file should exist')
        self.assertTrue(response['body']['compileUnits'][0]['compileUnitPath'] == main_source_path, 
                        'Real path to main.cpp matches')
 