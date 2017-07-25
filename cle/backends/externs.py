from . import Backend, Symbol
from ..utils import ALIGN_UP
from ..errors import CLEOperationError
from ..address_translator import AT

class ExternObject(Backend):
    def __init__(self, loader, map_size=0x8000):
        super(ExternObject, self).__init__('cle##externs', loader=loader)
        self.next_addr = 0
        self.map_size = map_size
        self.set_arch(loader.main_object.arch)
        self.memory.add_backer(0, '\0'*map_size)
        self.provides = 'extern-address space'


    def make_extern(self, name, alignment=8):
        try:
            return self._symbol_cache[name]
        except KeyError:
            pass

        addr = self.allocate(1, alignment=alignment)
        new_symbol = Symbol(self, name, AT.from_mva(addr, self).to_rva(), 1, Symbol.TYPE_FUNCTION)
        new_symbol.is_export = True

        self._symbol_cache[name] = new_symbol
        return new_symbol

    def get_pseudo_addr(self, name):
        return self.make_extern(name).rebased_addr

    def allocate(self, size=1, alignment=8):
        addr = ALIGN_UP(self.next_addr, alignment)
        self.next_addr = addr + size
        if self.next_addr > self.map_size:
            raise CLEOperationError("Ran out of room in the extern object...! Report this as a bug.")
        return addr + self.mapped_base

    @property
    def max_addr(self):
        return AT.from_rva(self.map_size, self).to_mva()

class KernelObject(Backend):
    def __init__(self, loader, map_size=0x8000):
        super(KernelObject, self).__init__('cle##kernel', loader=loader)
        self.map_size = map_size
        self.set_arch(loader.main_object.arch)
        self.memory.add_backer(0, '\0'*map_size)
        self.provides = 'kernel space'

    def add_name(self, name, addr):
        self._symbol_cache[name] = Symbol(self, name, AT.from_mva(addr, self).to_rva(), 1, Symbol.TYPE_FUNCTION)

    @property
    def max_addr(self):
        return AT.from_rva(self.map_size, self).to_mva()