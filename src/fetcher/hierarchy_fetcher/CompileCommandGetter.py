import json, shlex
from io import FileIO
from os.path import join
from src.model.core.SourceFile import SourceFile
from os.path import join


class CompileCommandGetter:

    def __init__(self, compile_commands_path: str) -> None:
        self.compile_commands_json: list[dict[str, str]] = self.__get_json(compile_commands_path)
        self.commands: dict[str, str] = {}
        self.__setup_commands()

    class CompileCommandError(Exception):
        pass

    def __get_json(self, path: str) -> list[dict[str, str]]:
        path = join(path, "build", "compile_commands.json")
        json_file: FileIO
        try:
            with open(path, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Did not find compile_commands.json file in project working directory\n {path}")
        
    def __setup_commands(self):
        command_object: dict[str, str]
        for command_object in self.compile_commands_json:
            if "command" not in command_object:
                raise self.CompileCommandError(f"Command Object {command_object} does not contain command")
            self.commands[self.__get_ofile_path(command_object["command"], command_object["directory"])] = command_object["command"]

    def __get_name_from_path(self, path: str) -> str:
        name: str = path.split("/")[-1]
        return name.removesuffix(".o")

    def __get_ofile_path(self, command: str, dir: str) -> str:
        args: list[str] = shlex.split(command)
        for i in range(args.__len__() - 1):
            if args[i] == "-o":
                return join(dir, args[i+1])
        raise self.CompileCommandError(f"no object file path found in compile-command")

    def get_compile_command(self, source_file: SourceFile) -> str:
        ofilepath = source_file.path
        if ofilepath not in self.commands:
            raise self.CompileCommandError(f"Source file does not have a stored command \n {ofilepath}")
        return self.commands[ofilepath]
    
    def generate_hierarchy_command(self, source_file: SourceFile) -> str:
        origin_command: str = self.get_compile_command(source_file)
        args: list[str] = shlex.split(origin_command)
        delindex: int = -1
        for i in range(len(args)):
            if args[i] == "-o":
                delindex = i
        if delindex == -1:
            raise self.CompileCommandError(f"no object file path found in compile-command \n {source_file.path}")
        else:
            del args[delindex: delindex + 2]
        args.append("-H")
        args.append("-M")
        return shlex.join(args)

    def get_all_opaths(self) -> list[str]:
        command_object: dict[str, str]
        opaths: list[str] = []
        for command_object in self.compile_commands_json:
            opaths.append(self.__get_ofile_path(command_object["command"], command_object["directory"]))
        return opaths
