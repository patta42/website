
"""
Some useful functions
"""

import inspect
from pprint import pprint

def add_css_class(css_string, css_class):
    css_classes = css_string.split(' ')
    try:
        for cls in css_class:
            if not cls in css_classes:
                css_classes.append(cls)
    except TypeError:
        if not css_class in css_classes:
            css_classes.append(css_class)

    return ' '.join(css_classes)

def remove_css_class(css_string, css_class):
    css_classes = css_string.split(' ')
    try:
        css_classes.remove(css_class)
    except ValueError:
        pass
    return ' '.join(css_classes)


def update_if_not_defined(dct, key, default):
    """
    performs dct.update({key : default}) if key not in dct or dct[key] is None
    """
    val = dct.get(key, None)
    if val is None:
        dct.update({key:default})

    return dct

def debug(obj, out, label = None):
    print ('\n\n--------------------------------------------------')
    print ('  Debug output')
    print ('--------------------------------------------------')
    print ('I am {}'.format(obj))
    print ('In method: {}'.format(inspect.stack()[1][3]))
    print ('Called from: {}'.format(inspect.stack()[2][3]))
    if label:
        print ('Now showing: {}'.format(label))
    pprint (out)
    print('---------------- End debug -----------------------\n')


def get_model_verbose_name(model):
    try:
        return model.get_verbose_name()
    except AttributeError:
        return model._meta.verbose_name

LIST_OF_ELEMENTS = [
    ('H', 'H (Wasserstoff)'),
    ('He', 'He (Helium)'),
    ('Li', 'Li (Lithium)'),
    ('Be', 'Be (Beryllium)'),
    ('B', 'B (Bor)'),
    ('C', 'C (Kohlenstoff)'),
    ('N', 'N (Stickstoff)'),
    ('O', 'O (Sauerstoff)'),
    ('F', 'F (Fluor)'),
    ('Ne', 'Ne (Neon)'),
    ('Na', 'Na (Natrium)'),
    ('Mg', 'Mg (Magnesium)'),
    ('Al', 'Al (Aluminium)'),
    ('Si', 'Si (Silicium)'),
    ('P', 'P (Phosphor)'),
    ('S', 'S (Schwefel)'),
    ('Cl', 'Cl (Chlor)'),
    ('Ar', 'Ar (Argon)'),
    ('K', 'K (Kalium)'),
    ('Ca', 'Ca (Calcium)'),
    ('Sc', 'Sc (Scandium)'),
    ('Ti', 'Ti (Titan)'),
    ('V', 'V (Vanadium)'),
    ('Cr', 'Cr (Chrom)'),
    ('Mn', 'Mn (Mangan)'),
    ('Fe', 'Fe (Eisen)'),
    ('Co', 'Co (Cobalt)'),
    ('Ni', 'Ni (Nickel)'),
    ('Cu', 'Cu (Kupfer)'),
    ('Zn', 'Zn (Zink)'),
    ('Ga', 'Ga (Gallium)'),
    ('Ge', 'Ge (Germanium)'),
    ('As', 'As (Arsen)'),
    ('Se', 'Se (Selen)'),
    ('Br', 'Br (Brom)'),
    ('Kr', 'Kr (Krypton)'),
    ('Rb', 'Rb (Rubidium)'),
    ('Sr', 'Sr (Strontium)'),
    ('Y', 'Y (Yttrium)'),
    ('Zr', 'Zr (Zirconium)'),
    ('Nb', 'Nb (Niob)'),
    ('Mo', 'Mo (Molybdän)'),
    ('Tc', 'Tc (Technetium)'),
    ('Ru', 'Ru (Ruthenium)'),
    ('Rh', 'Rh (Rhodium)'),
    ('Pd', 'Pd (Palladium)'),
    ('Ag', 'Ag (Silber)'),
    ('Cd', 'Cd (Cadmium)'),
    ('In', 'In (Indium)'),
    ('Sn', 'Sn (Zinn)'),
    ('Sb', 'Sb (Antimon)'),
    ('Te', 'Te (Tellur)'),
    ('I', 'I (Iod)'),
    ('Xe', 'Xe (Xenon)'),
    ('Cs', 'Cs (Caesium)'),
    ('Ba', 'Ba (Barium)'),
    ('La', 'La (Lanthan)'),
    ('Ce', 'Ce (Cer)'),
    ('Pr', 'Pr (Praseodym)'),
    ('Nd', 'Nd (Neodym)'),
    ('Pm', 'Pm (Promethium)'),
    ('Sm', 'Sm (Samarium)'),
    ('Eu', 'Eu (Europium)'),
    ('Gd', 'Gd (Gadolinium)'),
    ('Tb', 'Tb (Terbium)'),
    ('Dy', 'Dy (Dysprosium)'),
    ('Ho', 'Ho (Holmium)'),
    ('Er', 'Er (Erbium)'),
    ('Tm', 'Tm (Thulium)'),
    ('Yb', 'Yb (Ytterbium)'),
    ('Lu', 'Lu (Lutetium)'),
    ('Hf', 'Hf (Hafnium)'),
    ('Ta', 'Ta (Tantal)'),
    ('W', 'W (Wolfram)'),
    ('Re', 'Re (Rhenium)'),
    ('Os', 'Os (Osmium)'),
    ('Ir', 'Ir (Iridium)'),
    ('Pt', 'Pt (Platin)'),
    ('Au', 'Au (Gold)'),
    ('Hg', 'Hg (Quecksilber)'),
    ('Tl', 'Tl (Thallium)'),
    ('Pb', 'Pb (Blei)'),
    ('Bi', 'Bi (Bismut)'),
    ('Po', 'Po (Polonium)'),
    ('At', 'At (Astat)'),
    ('Rn', 'Rn (Radon)'),
    ('Fr', 'Fr (Francium)'),
    ('Ra', 'Ra (Radium)'),
    ('Ac', 'Ac (Actinium)'),
    ('Th', 'Th (Thorium)'),
    ('Pa', 'Pa (Protactinium)'),
    ('U', 'U (Uran)'),
    ('Np', 'Np (Neptunium)'),
    ('Pu', 'Pu (Plutonium)'),
    ('Am', 'Am (Americium)'),
    ('Cm', 'Cm (Curium)'),
    ('Bk', 'Bk (Berkelium)'),
    ('Cf', 'Cf (Californium)'),
    ('Es', 'Es (Einsteinium)'),
    ('Fm', 'Fm (Fermium)'),
    ('Md', 'Md (Mendelevium)'),
    ('No', 'No (Nobelium)'),
    ('Lr', 'Lr (Lawrencium)'),
    ('Rf', 'Rf (Rutherfordium)'),
    ('Db', 'Db (Dubnium)'),
    ('Sg', 'Sg (Seaborgium)'),
    ('Bh', 'Bh (Bohrium)'),
    ('Hs', 'Hs (Hassium)'),
    ('Mt', 'Mt (Meitnerium)'),
    ('Ds', 'Ds (Darmstadtium)'),
    ('Rg', 'Rg (Roentgenium)'),
    ('Cn', 'Cn (Copernicium)'),
    ('Nh', 'Nh (Nihonium)'),
    ('Fl', 'Fl (Flerovium)'),
    ('Mc', 'Mc (Moscovium)'),
    ('Lv', 'Lv (Livermorium)'),
    ('Ts', 'Ts (Tenness)'),
    ('Og', 'Og (Oganesson)')
]
