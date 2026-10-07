/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

/// This crate gives the same memory layout as `MethodInArgPtr` in the C++ implementation.
///
/// The C++ type is defined in `score/mw/com/impl/methods/method_signature_element_ptr.h` as
/// `MethodInArgPtr<Type> = MethodSignatureElementPtr<Type>`.
///
/// It can be used for FFI bindings where `MethodInArgPtr` is needed. It does not provide any
/// functionality beyond memory layout compatibility: in particular the C++ type is move-only and
/// its destructor clears the referenced `ptr_active_` flag. Lifetime management of that flag stays
/// with the C++ side and must be performed through the C++ operators, not by dropping this
/// layout-only Rust mirror.
use core::fmt::Debug;

/// Memory layout mirror of `score::mw::com::impl::MethodSignatureElementPtr<SignatureElement>`.
///
/// The C++ members, in declaration order, are:
/// `SignatureElement* element_ptr_; bool& ptr_active_; std::size_t queue_position_;`
/// A C++ reference is ABI-equivalent to a pointer, so `ptr_active_` is mirrored as `*mut bool`.
#[repr(C)]
pub struct MethodInArgPtr<T> {
    // `SignatureElement* element_ptr_`
    _element_ptr: *mut T,
    // `bool& ptr_active_`
    _ptr_active: *mut bool,
    // `std::size_t queue_position_`
    _queue_position: usize,
}

impl<T> Debug for MethodInArgPtr<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.debug_struct("MethodInArgPtr").finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use test_helper_size_ffi_rs::MethodInArgPtrLola;
    use test_utils_rs::*;

    #[test]
    fn test_method_in_arg_ptr_int32_size() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        verify_size_and_align!(MethodInArgPtr<i32>, cpp_size, "MethodInArgPtr<i32>");
    }

    #[test]
    fn test_method_in_arg_ptr_user_defined_type_size() {
        let cpp_size = MethodInArgPtrLola::get_user_defined_type();
        verify_size_and_align!(MethodInArgPtr<UserType>, cpp_size, "MethodInArgPtr<UserType>");
    }

    #[test]
    fn test_method_in_arg_ptr_layout_independent_of_element_type() {
        let int32_size = MethodInArgPtrLola::get_int32();
        let user_defined_type_size = MethodInArgPtrLola::get_user_defined_type();
        assert_eq!(
            int32_size.size, user_defined_type_size.size,
            "MethodInArgPtr size depends on element type!"
        );
        assert_eq!(
            int32_size.align, user_defined_type_size.align,
            "MethodInArgPtr alignment depends on element type!"
        );
    }

    #[test]
    #[should_panic(expected = "size mismatch")]
    fn test_negative_method_in_arg_ptr_size_mismatch() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        let incorrect = cpp_size.size + 1;
        assert_eq!(incorrect, cpp_size.size, "MethodInArgPtr size mismatch!");
    }

    #[test]
    #[should_panic(expected = "align mismatch")]
    fn test_negative_method_in_arg_ptr_align_mismatch() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        let incorrect = cpp_size.align + 1;
        assert_eq!(incorrect, cpp_size.align, "MethodInArgPtr align mismatch!");
    }
}
