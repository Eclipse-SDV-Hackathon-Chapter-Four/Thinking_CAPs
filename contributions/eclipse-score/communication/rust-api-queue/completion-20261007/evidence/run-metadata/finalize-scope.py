from pathlib import Path
import os,signal,time,json,hashlib,datetime,subprocess
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'workspaces/integrated'
while True:
 p=Path('/proc/1705121/stat')
 if not p.exists() or p.read_text().split(') ',1)[1].split()[0]=='Z': break
 time.sleep(1)
result=json.loads((ROOT/'complete-host-build/native-result.json').read_text())
progress=json.loads((ROOT/'complete-progress.json').read_text())
progress.append({'check':'host-build','exit_code':0 if result['passed'] else 1,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_epoch':'d887 before final scope documentation'})
(ROOT/'complete-progress.json').write_text(json.dumps(progress,indent=2)+'\n')
assert b'communication-complete-3c7jhdey/complete-pipeline.py' in Path('/proc/1263655/cmdline').read_bytes()
os.kill(1263655,signal.SIGTERM); os.kill(1263655,signal.SIGCONT)
p=WORK/'score/mw/com/rust/score_com_concept/concept.rs'; s=p.read_text(); old='''    /// it. The LoLa backend observes every service type present in the loaded configuration
    /// (including add-on configurations merged before the stream is opened), with any concrete
    /// instance id; service types that are not configured are not observed.'''; new='''    /// it. The LoLa backend observes service types with a configured LoLa instance deployment
    /// (including add-on configurations merged before the stream is opened), using that deployment's
    /// configured quality level and any concrete instance id. A type declaration without such a
    /// deployment, another binding, or an unconfigured interface type is outside this scope.'''; assert old in s; p.write_text(s.replace(old,new))
p=WORK/'score/mw/com/impl/rust/com-api/com-api-runtime-lola/service_stream.rs'; s=p.read_text(); old='''//! type present in the loaded native configuration. Each watch reports the complete set of currently offered provider
//! instances of that type, including provider instances whose concrete instance id is absent from the consumer's'''; new='''//! type with a LoLa instance deployment in the loaded native configuration. The deployment supplies the configured
//! quality level; type declarations without such a deployment are not observed. Each watch reports currently offered
//! provider instances of that type, including provider instances whose concrete instance id is absent from the consumer's'''; assert old in s; p.write_text(s.replace(old,new))
p=WORK/'score/mw/com/rust/design/high_level_design_detail.md'; s=p.read_text(); s=s.replace('Interface-independent identification (interface id + instance specifier) of an available service, yielded by discovery across configured LoLa service types','Owned interface name/version, binding, service id and observed instance id of an available service, yielded by discovery across configured LoLa deployments'); old='The LoLa implementation watches service types loaded when the stream opens, including provider instances absent from the consumer manifest.'; new='The LoLa implementation watches service types with a configured LoLa instance deployment when the stream opens, using the deployment\'s configured quality level. Provider instances may be absent from the consumer manifest; type declarations without a LoLa instance deployment are outside this scope.'; assert old in s; p.write_text(s.replace(old,new))
p=WORK/'score/mw/com/rust/doc/user_facing_api_examples.md'; s=p.read_text(); anchor='### InstanceSpecifier'; assert anchor in s; example='''### Observe Configured LoLa Services

`Runtime::find_all_services()` observes interfaces with a configured LoLa instance deployment, using the deployment's quality level. Provider instances may be absent from the consumer manifest. Type declarations without such a deployment, other bindings and unconfigured interface types are outside this scope. Merge add-on configurations before opening the stream to include their service types.

```rust
use futures::StreamExt;
use score_com::{Result, Runtime};

async fn observe_next_service(runtime: &impl Runtime) -> Result<()> {
    let mut services = runtime.find_all_services()?;
    if let Some(item) = services.next().await {
        let service = item?;
        println!("Available interface: {}", service.service_type_name());
    }
    Ok(()) // Drops the stream and unregisters its native watches.
}
```

An initial offer can produce the first item immediately. With no offer, the await remains pending; the LoLa stream does not yield `None`. Later offers are observed for the stream lifetime. Pending observations are coalesced by full service identity and withdrawn observations are discarded before polling. LoLa reports registration failures when creating the stream and produces no later error items. See the [production consumer example](../../test/basic_rust_api/all_services_stream/consumer_app.rs) for complete identity checks, withdrawal and re-offer behavior.

---

'''; p.write_text(s.replace(anchor,example+anchor,1))
patch=subprocess.check_output(['git','diff','HEAD','--binary'],cwd=WORK); (ROOT/'final-verification-candidate.patch').write_bytes(patch)
files=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=WORK,text=True).splitlines()
(ROOT/'final-verification-subjects.json').write_text(json.dumps({'baseline':subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK,text=True).strip(),'patch_sha256':hashlib.sha256(patch).hexdigest(),'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':f,'sha256':hashlib.sha256((WORK/f).read_bytes()).hexdigest(),'size_bytes':(WORK/f).stat().st_size} for f in files]},indent=2)+'\n')
(ROOT/'final-format-check-plan.json').write_bytes((ROOT/'complete-format-check-plan.json').read_bytes())
s=(ROOT/'complete-pipeline.py').read_text().replace('complete-','final-'); (ROOT/'final-pipeline.py').write_text(s)
p=ROOT/'auxiliary-checks.py'; s=p.read_text().replace('complete-ownership-regression','final-ownership-regression').replace('complete-candidate.patch','final-verification-candidate.patch'); p.write_text(s)
p=ROOT/'export-packet.py'; s=p.read_text().replace('complete-subjects.json','final-verification-subjects.json').replace('complete-candidate.patch','final-verification-candidate.patch').replace("('complete-'+name)","('final-'+name)").replace("('complete-','complete-progress.json')","('final-','final-progress.json')"); p.write_text(s)
print('FINAL SCOPE SOURCE',hashlib.sha256(patch).hexdigest(),flush=True)
subprocess.run(['python3',str(ROOT/'final-pipeline.py')],check=True)
