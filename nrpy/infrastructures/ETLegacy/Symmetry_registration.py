"""
Registration of symmetry conditions for gridfunctions.

Author: Zachariah B. Etienne
        zachetie **at** gmail **dot* com
"""
import nrpy.grid as gri
import nrpy.c_function as cfc
from nrpy.infrastructures.ETLegacy import schedule_ccl


def register_CFunction_Symmetry_registration_oldCartGrid3D(
    thorn_name: str,
) -> None:
    """
    Register symmetries for a NRPy+ generated Cactus thorn.

    This function takes the name of a NRPy+-generated thorn and
    registers symmetry properties for its associated grid functions.

    :param thorn_name: The name of the thorn generated by NRPy+.
    :return: None
    """
    includes = ["cctk.h", "cctk_Arguments.h", "cctk_Parameters.h", "Symmetry.h"]
    desc = f"Register symmetries for NRPy+-generated thorn {thorn_name}"
    c_type = "void"
    name = f"{thorn_name}_Symmetry_registration_oldCartGrid3D"
    params = "CCTK_ARGUMENTS"

    body = f"""  DECLARE_CCTK_ARGUMENTS_{name};
  DECLARE_CCTK_PARAMETERS;

  // Stores gridfunction parity across x=0, y=0, and z=0 planes, respectively
  int sym[3];

  // Next register parities for each gridfunction based on its name
  //    (to ensure this algorithm is robust, gridfunctions with integers
  //     in their base names are forbidden in NRPy+).
"""

    for gfname, gf in gri.glb_gridfcs_dict.items():
        # We only apply symmetries to evolved gridfunctions.
        if gf.group == "EVOL":
            body += """
  // Default to scalar symmetry:
  sym[0] = 1; sym[1] = 1; sym[2] = 1;
  // Now modify sym[0], sym[1], and/or sym[2] as needed
  //    to account for gridfunction parity across
  //    x=0, y=0, and/or z=0 planes, respectively
"""
            if len(gfname) > 2 and gfname[-3].isdigit():
                raise ValueError(
                    "Sorry, gridfunctions of rank 3 or greater not supported."
                )
            elif len(gfname) > 3 and gfname[-2].isdigit():  # Rank 2
                symidx0 = gfname[-2]
                symidx1 = gfname[-1]
                body += f"  sym[{symidx0}] *= -1;\n"
                body += f"  sym[{symidx1}] *= -1;\n"
            elif gfname[-1].isdigit():  # Rank 1
                symidx = gfname[-1]
                body += f"  sym[{symidx}] *= -1;\n"
            elif not gfname[-1].isdigit():  # Rank 0
                body += "  // (this gridfunction is a scalar -- no need to change default sym[]'s!)\n"
            else:
                raise ValueError(
                    f"Don't know how you got this far with a gridfunction named {gfname}, but I'll take no more of this nonsense. \
                                  Please follow best-practices and rename your gridfunction to be more descriptive."
                )

            body += f'  SetCartSymVN(cctkGH, sym, "{thorn_name}::{gfname}");\n'

    ET_schedule_bin_entry = (
        "BASEGRID",
        """
schedule FUNC_NAME at BASEGRID as Symmetry_registration
{
  LANG: C
  OPTIONS: Global
} "Register symmetries, the CartGrid3D way."
""",
    )
    cfc.register_CFunction(
        subdirectory=thorn_name,
        includes=includes,
        desc=desc,
        c_type=c_type,
        name=name,
        params=params,
        body=body,
        ET_thorn_name=thorn_name,
        ET_schedule_bins_entries=[ET_schedule_bin_entry],
    )
