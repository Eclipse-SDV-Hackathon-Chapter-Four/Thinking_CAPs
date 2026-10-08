from pathlib import Path
import subprocess,json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'workspaces/integrated'
p=WORK/'score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.cpp';s=p.read_text();anchor='/// \\brief Stop an ongoing service discovery operation and delete the handle'
assert anchor in s
owned='''/// \\brief Start Specific discovery and transfer the boxed Rust callback on success
/// \\details The original mw_com_start_find_service symbol retains its baseline ownership
/// semantics. This additive entry point releases an accepted callback when native discovery
/// relinquishes it; a rejected registration leaves ownership with the Rust caller.
void* mw_com_start_find_service_owned(const FatPtr* callback, InstanceSpecifier* instance_spec)
{
    if (callback == nullptr || instance_spec == nullptr)
    {
        return nullptr;
    }

    auto ownership = std::make_shared<DiscoveryCallbackOwnership>(*callback);
    auto result = Runtime::getInstance().GetServiceDiscovery().StartFindService(
        [ownership](ServiceHandleContainer<HandleType> handles, FindServiceHandle handle) noexcept {
            RustBoxedCallable<void, ServiceHandleContainer<HandleType>, FindServiceHandle>::invoke(
                ownership->pointer, std::move(handles), handle);
        },
        std::move(*instance_spec));
    ownership->transferred = result.has_value();
    if (result.has_value())
    {
        return new FindServiceHandle{std::move(result).value()};
    }
    return nullptr;
}

'''
s=s.replace(anchor,owned+anchor,1);p.write_text(s)
p=WORK/'score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs';s=p.read_text();s=s.replace('mw_com_start_find_service(', 'mw_com_start_find_service_owned(');s=s.replace('Wrapper around mw_com_start_find_service','Wrapper around mw_com_start_find_service_owned').replace('returned by mw_com_start_find_service','returned by mw_com_start_find_service_owned');p.write_text(s)
p=WORK/'score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi.rs';s=p.read_text();s=s.replace('/// `FindServiceCallable, check its `unsafe` constructor for the full contract.','/// `FindServiceCallable`; check its `unsafe` constructor for the full contract.');s=s.replace('''    /// The returned handle must eventually be passed to `stop_find_service`.''','''    /// A non-null handle transfers callback ownership to the bridge. A null handle leaves
    /// ownership with the caller. The returned handle must eventually be passed to
    /// `stop_find_service`; the bridge disposes its accepted callback after native teardown.''',1)
old='''    /// `fat_ptr` must be a valid, whose underlying closure has the signature
    /// `FnMut(HandleContainer, NativeFindServiceHandle)` and must remain valid for
    /// as long as the returned `FindServiceCallable` (and the find-service operation
    /// registered with it) is alive.'''
new='''    /// `fat_ptr` must come from `Box::into_raw` for a
    /// `Box<dyn FnMut(HandleContainer, NativeFindServiceHandle) + Send + 'static>`.
    /// It must be live, uniquely owned and used for at most one successful registration.
    /// A successful registration transfers ownership to the bridge; the caller must not
    /// reclaim, invoke or register it again. On rejection the caller retains ownership.
    /// Before registration the allocation must remain live for all uses of this wrapper.
    /// The bridge must serialize callback invocations and dispose the box only after
    /// the native operation relinquishes it, including any deferred teardown.'''
assert old in s;s=s.replace(old,new);p.write_text(s)
p=WORK/'score/mw/com/impl/rust/com-api/com-api-ffi-lola/callback_ownership_test.cpp';s=p.read_text().replace('Copyright (c) 2025','Copyright (c) 2026');s=s.replace('''    state_deletions = 0U;
    auto native = std::make_shared<SubscriptionStateHandlerOwnership>(FatPtr{});''','''    state_deletions = 0U;
    discovery_deletions = 0U;
    auto native = std::make_shared<SubscriptionStateHandlerOwnership>(FatPtr{});
    auto native_discovery = std::make_shared<DiscoveryCallbackOwnership>(FatPtr{});''');s=s.replace('''        registration->transferred = true;
    }
    EXPECT_EQ(state_deletions, 0U);
    native.reset();
    EXPECT_EQ(state_deletions, 1U);''','''        registration->transferred = true;
        auto discovery_registration = native_discovery;
        discovery_registration->transferred = true;
    }
    EXPECT_EQ(state_deletions, 0U);
    EXPECT_EQ(discovery_deletions, 0U);
    native.reset();
    native_discovery.reset();
    EXPECT_EQ(state_deletions, 1U);
    EXPECT_EQ(discovery_deletions, 1U);''');p.write_text(s)
# Fresh production coverage for the Specific discovery path.
plan=json.loads((ROOT/'serial-integrations-plan.json').read_text());plan['checks'].append({'kind':'test','targets':['//score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test:test_com_api_async'],'reason':'Exercise updated owned Specific discovery FFI in the native production integration'});(ROOT/'owned-serial-integrations-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
# Keep every source epoch and its results distinct.
s=(ROOT/'final-pipeline.py').read_text().replace('final-','owned-').replace('"extended-pipeline.py"','"owned-extended-pipeline.py"');s=s.replace("else name+'-plan.json'", "else 'owned-serial-integrations-plan.json' if name=='serial-integrations' else name+'-plan.json'");(ROOT/'owned-pipeline.py').write_text(s)
s=(ROOT/'extended-pipeline.py').read_text().replace("'extended-'","'owned-extended-'").replace('extended-progress.json','owned-extended-progress.json');(ROOT/'owned-extended-pipeline.py').write_text(s)
(ROOT/'owned-format-check-plan.json').write_bytes((ROOT/'final-format-check-plan.json').read_bytes())
# Format first, then capture immutable verification source.
subprocess.run(['python3',str(ROOT/'supplementary_launcher.py'),'--workspace',str(WORK),'--plan',str(ROOT/'format-apply-plan.json'),'--output',str(ROOT/'owned-format-apply')],check=True)
patch=subprocess.check_output(['git','diff','HEAD','--binary'],cwd=WORK);(ROOT/'owned-candidate.patch').write_bytes(patch)
files=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=WORK,text=True).splitlines()
(ROOT/'owned-subjects.json').write_text(json.dumps({'baseline':subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK,text=True).strip(),'patch_sha256':hashlib.sha256(patch).hexdigest(),'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':f,'sha256':hashlib.sha256((WORK/f).read_bytes()).hexdigest(),'size_bytes':(WORK/f).stat().st_size} for f in files]},indent=2)+'\n')
p=ROOT/'auxiliary-checks.py';s=p.read_text().replace('final-ownership-regression','owned-ownership-regression').replace('final-verification-candidate.patch','owned-candidate.patch');p.write_text(s)
p=ROOT/'export-packet.py';s=p.read_text().replace('final-verification-subjects.json','owned-subjects.json').replace('final-verification-candidate.patch','owned-candidate.patch').replace("('final-'+name)","('owned-'+name)").replace("('final-','final-progress.json')","('owned-','owned-progress.json')").replace("('extended-','extended-progress.json')","('owned-extended-','owned-extended-progress.json')").replace('final-host-build','owned-host-build');p.write_text(s)
print('OWNED SPECIFIC SOURCE',hashlib.sha256(patch).hexdigest(),flush=True)
subprocess.run(['python3',str(ROOT/'owned-pipeline.py')],check=True)
