"""
Registration of grid functions with the MoL (method of lines) thorn.

Author: Zachariah B. Etienne
        zachetie **at** gmail **dot* com
"""
import nrpy.c_function as cfc
from nrpy.infrastructures.ETLegacy import schedule_ccl


def register_CFunction_MoL_registration(thorn_name: str) -> None:
    """
    Register evolved gridfunctions and RHSs with the MoL timestepper in the Einstein Toolkit.

    Registers the evolution and RHS gridfunction groups with the Method of Lines
    (MoL) timestepper within the Einstein Toolkit.

    :param thorn_name: The name of the thorn generated by NRPy+.
    :return: None
    """
    includes = ["stdio.h", "cctk.h", "cctk_Arguments.h", "cctk_Parameters.h"]
    desc = """Register evolved gridfunctions & RHSs
with the Method of Lines timestepper
MoL (the Einstein Toolkit Method of Lines thorn)
(MoL thorn, found in arrangements/CactusBase/MoL).
MoL documentation located in arrangements/CactusBase/MoL/doc
"""
    c_type = "void"
    name = f"{thorn_name}_MoL_registration"
    params = "CCTK_ARGUMENTS"
    body = f"""DECLARE_CCTK_ARGUMENTS_{name};
DECLARE_CCTK_PARAMETERS;

CCTK_INT ierr = 0, group, rhs;

// Register evolution & RHS gridfunction groups with MoL, so it knows
//  how to perform the appropriate timestepping

group = CCTK_GroupIndex("{thorn_name}::evol_variables");
rhs = CCTK_GroupIndex("{thorn_name}::evol_variables_rhs");
ierr += MoLRegisterEvolvedGroup(group, rhs);

if (ierr) CCTK_ERROR("Problems registering with MoL");
"""

    ET_schedule_bin_entry = (
        "MoL_Register",
        """
schedule FUNC_NAME in MoL_Register
{
  LANG: C
  OPTIONS: META
} "Register variables for MoL"
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
