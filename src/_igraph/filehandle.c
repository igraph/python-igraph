/* -*- mode: C -*-  */
/* 
   IGraph library.
   Copyright (C) 2010-2012  Tamas Nepusz <ntamas@gmail.com>
   
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc.,  51 Franklin Street, Fifth Floor, Boston, MA 
   02110-1301 USA

*/

#include "filehandle.h"
#include "pyhelpers.h"

#ifndef PYPY_VERSION
static int igraphmodule_i_filehandle_init_cpython_3(igraphmodule_filehandle_t* handle,
        PyObject* object, char* mode) {
    int fp;

    if (object == 0 || PyLong_Check(object)) {
        PyErr_SetString(PyExc_TypeError, "string or file-like object expected");
        return 1;
    }

    handle->fp = 0;
    handle->need_close = 0;
    handle->object = 0;

    if (PyBaseString_Check(object)) {
        /* We have received a string; we need to open the file denoted by this
         * string now and mark that we opened the file ourselves (so we need
         * to close it when igraphmodule_filehandle_destroy is invoked). */
        handle->object = igraphmodule_PyFile_FromObject(object, mode);
        if (handle->object == 0) {
            /* Could not open the file; just return an error code because an
             * exception was raised already */
            return 1;
        }
        /* Remember that we need to close the file ourselves */
        handle->need_close = 1;
    } else {
        /* This is probably a file-like object; store a reference for it and
         * we will handle it later */
        handle->object = object;
        Py_INCREF(handle->object);
    }

    /* At this stage, handle->object is something we can handle.
     * We have to call PyObject_AsFileDescriptor instead
     * and then fdopen() it to get the corresponding FILE* object.
     */
    fp = PyObject_AsFileDescriptor(handle->object);
    if (fp == -1) {
        igraphmodule_filehandle_destroy(handle);
        /* This already called Py_DECREF(handle->object), no need to call it */
        return 1;
    }
    handle->fp = fdopen(fp, mode);
    if (handle->fp == 0) {
        igraphmodule_filehandle_destroy(handle);
        /* This already called Py_DECREF(handle->object), no need to call it */
        PyErr_SetString(PyExc_RuntimeError, "fdopen() failed unexpectedly");
        return 1;
    }

    return 0;
}
#else /* PYPY_VERSION */
static int igraphmodule_i_filehandle_init_pypy_3(igraphmodule_filehandle_t* handle,
        PyObject* object, char* mode) {
    int fp;

    if (object == 0 || PyLong_Check(object)) {
        PyErr_SetString(PyExc_TypeError, "string or file-like object expected");
        return 1;
    }

    handle->fp = 0;
    handle->need_close = 0;
    handle->object = 0;

    if (PyBaseString_Check(object)) {
        /* We have received a string; we need to open the file denoted by this
         * string now and mark that we opened the file ourselves (so we need
         * to close it when igraphmodule_filehandle_destroy is invoked). */
        handle->object = igraphmodule_PyFile_FromObject(object, mode);
        if (handle->object == 0) {
            /* Could not open the file; just return an error code because an
             * exception was raised already */
            return 1;
        }
        /* Remember that we need to close the file ourselves */
        handle->need_close = 1;
    } else {
        /* This is probably a file-like object; store a reference for it and
         * we will handle it later */
        handle->object = object;
        Py_INCREF(handle->object);
    }

    /* At this stage, handle->object is something we can handle.
     * We have to call PyObject_AsFileDescriptor instead
     * and then fdopen() it to get the corresponding FILE* object.
     */
    fp = PyObject_AsFileDescriptor(handle->object);
    if (fp == -1) {
        igraphmodule_filehandle_destroy(handle);
        /* This already called Py_DECREF(handle->object), no need to call it */
        return 1;
    }

    handle->fp = fdopen(fp, mode);
    if (handle->fp == 0) {
        igraphmodule_filehandle_destroy(handle);
        /* This already called Py_DECREF(handle->object), no need to call it */
        PyErr_SetString(PyExc_RuntimeError, "fdopen() failed unexpectedly");
        return 1;
    }

    return 0;
}
#endif

/**
 * \ingroup python_interface_filehandle
 * \brief Constructs a new file handle object from a Python object.
 *
 * \return 0 if everything was OK, 1 otherwise. An appropriate Python
 *   exception is raised in this case.
 */
int igraphmodule_filehandle_init(igraphmodule_filehandle_t* handle,
        PyObject* object, char* mode) {
#ifdef PYPY_VERSION
    return igraphmodule_i_filehandle_init_pypy_3(handle, object, mode);
#else
    return igraphmodule_i_filehandle_init_cpython_3(handle, object, mode);
#endif
}

/**
 * \ingroup python_interface_filehandle
 * \brief Destroys the file handle object.
 */
void igraphmodule_filehandle_destroy(igraphmodule_filehandle_t* handle) {
    PyObject *exc_type = 0, *exc_value = 0, *exc_traceback = 0;

    if (handle->fp != 0) {
        fflush(handle->fp);
        if (handle->need_close && !handle->object) {
            fclose(handle->fp);
        }
        handle->fp = 0;
    }
    
    if (handle->object != 0) {
        /* igraphmodule_PyFile_Close might mess up the stored exception, so let's
         * store the current exception state and restore it */
        PyErr_Fetch(&exc_type, &exc_value, &exc_traceback);
        if (handle->need_close) {
            if (igraphmodule_PyFile_Close(handle->object)) {
                PyErr_WriteUnraisable(Py_None);
            }
        }
        Py_DECREF(handle->object);
        PyErr_Restore(exc_type, exc_value, exc_traceback);
        exc_type = exc_value = exc_traceback = 0;
        handle->object = 0;
    }

    handle->need_close = 0;
}

/**
 * \ingroup python_interface_filehandle
 * \brief Returns the file encapsulated by the given \c igraphmodule_filehandle_t.
 */
FILE* igraphmodule_filehandle_get(const igraphmodule_filehandle_t* handle) {
    return handle->fp;
}

