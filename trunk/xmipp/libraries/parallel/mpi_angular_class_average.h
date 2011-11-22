/***************************************************************************
 * Authors:     AUTHOR_NAME (aerey@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/

#ifndef MPI_ANGULAR_CLASS_AVERAGE_H_
#define MPI_ANGULAR_CLASS_AVERAGE_H_

//mpirun -np 5 xmipp_mpi_angular_class_average --nJobs 70
#include <parallel/xmipp_mpi.h>
#include <data/xmipp_funcs.h>
#include <data/xmipp_program.h>
#include <data/metadata.h>

#include <data/xmipp_fftw.h>
#include <data/args.h>
#include <data/xmipp_image.h>
#include <data/filters.h>
#include <data/mask.h>
#include <data/polar.h>

//Tags already defined in xmipp
//#define TAG_WORK                     0
//#define TAG_STOP                     1
#define TAG_I_FINISH_WRITTING        12
#define TAG_MAY_I_WRITE              13
#define TAG_YES_YOU_MAY_WRITE        14
#define TAG_DO_NOT_DARE_TO_WRITE     15
#define TAG_I_AM_FREE                16

#define ArraySize 5

class ProgMpiAngularClassAverage : public XmippProgram
{
public:
    /**Number of job */
    int nJobs;

    /** status after am MPI call */
    MPI_Status status;

    // Mpi node
    MpiNode *node;

    // Metadata with the list of jobs
    MetaData mdJobList;

    /** Input and library docfiles */
    MetaData         DF, DFlib;
    /** metadata with classes which have experimental images applied to them */
    MetaData         DFclassesExp;
    /** Output rootnames */
    FileName         fn_out, fn_out1, fn_out2, fn_wien;
    /** Column numbers */
    std::string      col_select;
    /** Upper and lower absolute and relative selection limits */
    double           limit0, limitF, limitR;
    /** Flags wether to use limit0, limitF and limitR selection */
    bool             do_limit0, do_limitF, do_limitR0, do_limitRF;
    /** Flag whether to apply mirror operations. By default set to True */
    bool             do_mirrors;
    /** Flag whether also to write out class averages of random halves of the data */
    bool             do_split;
    /** Image dimensions before and after padding (only for Wiener correction) */
    int               paddim;
    /** Padding factor */
    double           pad;
    /** One empty image with correct dimensions */
    Image<double>    Iempty;
    /** Do NOT skip writing of selfiles */
    bool             write_selfiles;
    /** Number of 3d references */
    int              number_3dref;
    /** Delete auxiliary files from previous execution.
     * Alloc disk space for output stacks */
    bool             do_preprocess;
    /** Create block with average images filenames */
    bool             do_postprocess;
    /** Add output to existing files */
    bool             do_add;
    /** Wiener filter image */
    MultidimArray<double> Mwien;
    /** Selfiles containing all class averages */
    MetaData         SFclasses, SFclasses1, SFclasses2;

    /** Re-alignment of classes */

    /** Input file */
    FileName inFile, refGroup;
    /** Inner and outer radius for rotational alignment */
    int Ri, Ro;
    /** Number of iterations */
    int nr_iter;
    /** Convergence criterion */
    double eps;
    /** Search shift (shifts larger than this will be set to 0)*/
    double max_shift;
    /** Maximum allowed shift in last iteration (shifts larger than this will be set to 0)*/
    double max_shift_change, max_psi_change;
    /** transformers for all rings */
    Polar_fftw_plans global_plans;
    FourierTransformer global_transformer;
    MultidimArray<double> corr;

    /** Ctf group number */
    int ctfNum;
    /** 3D reference number */
    int ref3dNum;

    /** Image dimentions */
    int Xdim, Ydim, Zdim;
    /** Number of valid projection directions */
    size_t Ndim;


    ProgMpiAngularClassAverage(int argc, char **argv);

//    /** Redefine read */
//    void read(int argc, char** argv);

    void readParams();

    void defineParams();

    void run();

    /**
         */
    void mpi_process(int * Def_3Dref_2Dref_JobNo);

    /**
         */
    void mpi_produceSideInfo();

    /** Initialize variables, create infrastructure for mpi job submission, and delete output files.
         */
    void mpi_preprocess();

    /** Delete output files if they exist.
         */
    void deleteOutputFiles();

    /**
         */
    void mpi_postprocess();

    /** Compute list of parallel jobs to be performed
             */
    void createJobList();
};

#endif /* MPI_ANGULAR_CLASS_AVERAGE_H_ */



