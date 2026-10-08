{
  "data": [
    {
      "tag": "req mw_com_fta.ActivelyManipulateByProgrammParts",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 8,
        "column": 20
      },
      "name": "mw_com_fta.ActivelyManipulateByProgrammParts",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Actively manipulate by programm parts",
      "status": null
    },
    {
      "tag": "req mw_com_fta.AlgorithmicBug",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 16,
        "column": 20
      },
      "name": "mw_com_fta.AlgorithmicBug",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventOnlyPartiallyNotifiesConsumer"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Algorithmic Bug",
      "status": null
    },
    {
      "tag": "req mw_com_fta.AllocateClaimsToFewMemory",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 24,
        "column": 20
      },
      "name": "mw_com_fta.AllocateClaimsToFewMemory",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Allocate claims to few memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.BindingSelectionFaulty",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 32,
        "column": 20
      },
      "name": "mw_com_fta.BindingSelectionFaulty",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedOnWrongBinding"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Binding selection faulty",
      "status": null
    },
    {
      "tag": "req mw_com_fta.BlocksOnCaller",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 40,
        "column": 20
      },
      "name": "mw_com_fta.BlocksOnCaller",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodCallBlocksLongerThanExpected"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Method call blocks in message-passing at the caller side -> send blocked",
      "status": null
    },
    {
      "tag": "req mw_com_fta.BrokenAllocator",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 48,
        "column": 20
      },
      "name": "mw_com_fta.BrokenAllocator",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Broken allocator",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallBlocksOnCallee",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 56,
        "column": 20
      },
      "name": "mw_com_fta.CallBlocksOnCallee",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodCallBlocksLongerThanExpected"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Method call blocks in reply at the callee side -> send blocked ",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallBlocksOnUserHandler",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 64,
        "column": 20
      },
      "name": "mw_com_fta.CallBlocksOnUserHandler",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodCallBlocksLongerThanExpected"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Method call blocks in user-handler at the callee side",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallSignalledBeforeInArgsCompletelyProvided",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 72,
        "column": 20
      },
      "name": "mw_com_fta.CallSignalledBeforeInArgsCompletelyProvided",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Call signalled before InArgs completely provided",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallbackDangling",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 80,
        "column": 20
      },
      "name": "mw_com_fta.CallbackDangling",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callback dangling",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallbackIsNotStoredCorrectly",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 88,
        "column": 20
      },
      "name": "mw_com_fta.CallbackIsNotStoredCorrectly",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackNotInvokedDespiteSamplesAvailable"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callback is not stored correctly",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalledEventhoughStopfindserviceHasBeenCalled",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 96,
        "column": 20
      },
      "name": "mw_com_fta.CalledEventhoughStopfindserviceHasBeenCalled",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StartFindServiceCallbackCalledUnexpectedly"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Called eventhough StopFindService has been called",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalledReduandently",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 104,
        "column": 20
      },
      "name": "mw_com_fta.CalledReduandently",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StartFindServiceCallbackCalledUnexpectedly"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Called reduandently",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeConcurrentlyUpdatesResultAfterSignaling",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 112,
        "column": 20
      },
      "name": "mw_com_fta.CalleeConcurrentlyUpdatesResultAfterSignaling",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResultsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee concurrently updates result after signaling it",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeProvidedResultInWrongLayout",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 120,
        "column": 20
      },
      "name": "mw_com_fta.CalleeProvidedResultInWrongLayout",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResultsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee provided result in wrong layout",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeProvidedResultInWrongLocation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 128,
        "column": 20
      },
      "name": "mw_com_fta.CalleeProvidedResultInWrongLocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResultsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee provided result in wrong location",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeSignalledCallFinishedBeforeResultComplete",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 136,
        "column": 20
      },
      "name": "mw_com_fta.CalleeSignalledCallFinishedBeforeResultComplete",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResultsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee signalled call finished before or without providing result completely",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeUsedInArgsBeforeBeingProvided",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 144,
        "column": 20
      },
      "name": "mw_com_fta.CalleeUsedInArgsBeforeBeingProvided",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee used InArgs before being provided",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeUsedInArgsFromWrongLocation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 152,
        "column": 20
      },
      "name": "mw_com_fta.CalleeUsedInArgsFromWrongLocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee used InArgs from wrong location",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeUsedInArgsInWrongLayout",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 160,
        "column": 20
      },
      "name": "mw_com_fta.CalleeUsedInArgsInWrongLayout",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee used InArgs in wrong layout",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CalleeUsedInArgsWhileConcurrentlyUpdated",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 168,
        "column": 20
      },
      "name": "mw_com_fta.CalleeUsedInArgsWhileConcurrentlyUpdated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Callee used InArgs while concurrently updated",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallerProvidedInArgsInWrongLocation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 176,
        "column": 20
      },
      "name": "mw_com_fta.CallerProvidedInArgsInWrongLocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller provided InArgs in wrong location",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallerUsedResultBeforeFullyProvided",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 184,
        "column": 20
      },
      "name": "mw_com_fta.CallerUsedResultBeforeFullyProvided",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongReturnValueUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller used result before fully provided",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallerUsedResultFromWrongLocation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 192,
        "column": 20
      },
      "name": "mw_com_fta.CallerUsedResultFromWrongLocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongReturnValueUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller used result from wrong location",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallerUsedResultInWrongLayout",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 200,
        "column": 20
      },
      "name": "mw_com_fta.CallerUsedResultInWrongLayout",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongReturnValueUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller used result in wrong layout",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CallerUsedResultWhileConcurrentlyUpdated",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 208,
        "column": 20
      },
      "name": "mw_com_fta.CallerUsedResultWhileConcurrentlyUpdated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongReturnValueUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller used result while concurrently updated",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ChangingStateFails",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 216,
        "column": 20
      },
      "name": "mw_com_fta.ChangingStateFails",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.DoesNotFreeResourcesOnDestruction"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Changing state fails",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ConsumerLookedUpSizeInWrongLocation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 224,
        "column": 20
      },
      "name": "mw_com_fta.ConsumerLookedUpSizeInWrongLocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TheSizeReturnedIsBiggerThenTheActualValue"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Consumer looked up size in wrong location",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 232,
        "column": 20
      },
      "name": "mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Consumer uses an older slot, than he already has blocked in the previous access",
      "status": null
    },
    {
      "tag": "req mw_com_fta.CopyOnSendDoesNotDestroySampleallocateeptr",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 240,
        "column": 20
      },
      "name": "mw_com_fta.CopyOnSendDoesNotDestroySampleallocateeptr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventDoesNotFreeResources"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Copy on send does not destroy SampleAllocateePtr",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 248,
        "column": 20
      },
      "name": "mw_com_fta.DataTypeItselfIsAllocatedOnStack",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Data-Type itself is allocated on stack",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DependentPrepareOfferFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 256,
        "column": 20
      },
      "name": "mw_com_fta.DependentPrepareOfferFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferInconsistent"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "PrepareOffer on dependent elements failed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DependentPrepareOfferNotCalled",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 264,
        "column": 20
      },
      "name": "mw_com_fta.DependentPrepareOfferNotCalled",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferInconsistent"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "PrepareOffer on dependent elements not called",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DestructionOfSampleallocateeptrDoesNotTriggerStateChange",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 272,
        "column": 20
      },
      "name": "mw_com_fta.DestructionOfSampleallocateeptrDoesNotTriggerStateChange",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventDoesNotFreeResources"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Destruction of SampleAllocateePtr does not trigger state change",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DifferentlyConfiguredBetweenSkletonAndProxySide",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 280,
        "column": 20
      },
      "name": "mw_com_fta.DifferentlyConfiguredBetweenSkletonAndProxySide",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Differently configured between skleton and proxy side",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DirectAccessToDataViaAllocateePtr",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 288,
        "column": 20
      },
      "name": "mw_com_fta.DirectAccessToDataViaAllocateePtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventChangesUserData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Direct access to data",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DirectAccessToDataViaCopy",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 296,
        "column": 20
      },
      "name": "mw_com_fta.DirectAccessToDataViaCopy",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventChangesUserData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Direct access to data",
      "status": null
    },
    {
      "tag": "req mw_com_fta.DoesNotFreeMethodSignatureElement",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 304,
        "column": 20
      },
      "name": "mw_com_fta.DoesNotFreeMethodSignatureElement",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrFailsToFree"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Does not free method signature element",
      "status": null
    },
    {
      "tag": "req mw_com_fta.EventFieldIdReferencesWrongStorage",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 312,
        "column": 20
      },
      "name": "mw_com_fta.EventFieldIdReferencesWrongStorage",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SubscribeToWrongEvent"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Event/Field ID references wrong storage.",
      "status": null
    },
    {
      "tag": "req mw_com_fta.EventFieldNameMappingClash",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 320,
        "column": 20
      },
      "name": "mw_com_fta.EventFieldNameMappingClash",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SubscribeToWrongEvent"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Event/Field name mapping clash",
      "status": null
    },
    {
      "tag": "req mw_com_fta.EventfqidWronglyConstructed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 328,
        "column": 20
      },
      "name": "mw_com_fta.EventfqidWronglyConstructed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "EventFqId wrongly constructed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ExplicitUnsubscribeByUserFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 336,
        "column": 20
      },
      "name": "mw_com_fta.ExplicitUnsubscribeByUserFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.DoesNotUnsubscribe"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Explicit unsubscribe by user failed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.FileCorrupted",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 344,
        "column": 20
      },
      "name": "mw_com_fta.FileCorrupted",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.InMemoryConfigurationWrong"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "File corrupted",
      "status": null
    },
    {
      "tag": "req mw_com_fta.FilenameCreationFromConfigFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 352,
        "column": 20
      },
      "name": "mw_com_fta.FilenameCreationFromConfigFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedUnderWrongIds"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Filename creation from config failed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 360,
        "column": 20
      },
      "name": "mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Forwarded the wrong shared memory segment from the beginning",
      "status": null
    },
    {
      "tag": "req mw_com_fta.GenericTraceapiChangesData",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 368,
        "column": 20
      },
      "name": "mw_com_fta.GenericTraceapiChangesData",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventChangesUserData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Generic TraceAPI changes data",
      "status": null
    },
    {
      "tag": "req mw_com_fta.HoldsMoreSampleptrThanAnnounced",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 376,
        "column": 20
      },
      "name": "mw_com_fta.HoldsMoreSampleptrThanAnnounced",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Holds more SamplePtr than announced",
      "status": null
    },
    {
      "tag": "req mw_com_fta.HoldsMoreSampleptrThanConfigured",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 384,
        "column": 20
      },
      "name": "mw_com_fta.HoldsMoreSampleptrThanConfigured",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Holds more SamplePtr than configured",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InArgsCorruptedBy3rdParty",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 392,
        "column": 20
      },
      "name": "mw_com_fta.InArgsCorruptedBy3rdParty",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsUsed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "InArgs corrupted by 3d party",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InArgsUpdateAfterCall",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 400,
        "column": 20
      },
      "name": "mw_com_fta.InArgsUpdateAfterCall",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller updates InArgs concurrently after call signalling",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InArgsWrongLayout",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 408,
        "column": 20
      },
      "name": "mw_com_fta.InArgsWrongLayout",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodInArgsProvided"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Caller provided InArgs in wrong layout",
      "status": null
    },
    {
      "tag": "req mw_com_fta.IncreasingDecreasingRefCountFails",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 416,
        "column": 20
      },
      "name": "mw_com_fta.IncreasingDecreasingRefCountFails",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.DoesNotFreeResourcesOnDestruction"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Increasing / Decreasing ref-count fails",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InotifyReturnsWrongInformation",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 424,
        "column": 20
      },
      "name": "mw_com_fta.InotifyReturnsWrongInformation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StartFindServiceCallbackCalledUnexpectedly"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Inotify returns wrong information",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InstanceSpecifierResolutionBrokenNotOffered",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 432,
        "column": 20
      },
      "name": "mw_com_fta.InstanceSpecifierResolutionBrokenNotOffered",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Instance Specifier resolution broken",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InstanceSpecifierResolutionBrokenWrongBinding",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 440,
        "column": 20
      },
      "name": "mw_com_fta.InstanceSpecifierResolutionBrokenWrongBinding",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedOnWrongBinding"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Instance Specifier resolution broken",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InstanceSpecifierResolutionFaulty",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 448,
        "column": 20
      },
      "name": "mw_com_fta.InstanceSpecifierResolutionFaulty",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedUnderWrongIds"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Instance Specifier resolution faulty",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InstanceSpecifierResolutionLogicBroken",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 456,
        "column": 20
      },
      "name": "mw_com_fta.InstanceSpecifierResolutionLogicBroken",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CreationOfSkeletonNotPossible"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Instance Specifier resolution logic broken",
      "status": null
    },
    {
      "tag": "req mw_com_fta.InstancespecifierResolvedToWrongInstanceidentifier",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 464,
        "column": 20
      },
      "name": "mw_com_fta.InstancespecifierResolvedToWrongInstanceidentifier",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongServiceFound"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "InstanceSpecifier resolved to wrong InstanceIdentifier",
      "status": null
    },
    {
      "tag": "req mw_com_fta.IssueInLockFreeSychronization",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 472,
        "column": 20
      },
      "name": "mw_com_fta.IssueInLockFreeSychronization",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Issue in Lock-free Sychronization",
      "status": null
    },
    {
      "tag": "req mw_com_fta.JsonParserBroken",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 480,
        "column": 20
      },
      "name": "mw_com_fta.JsonParserBroken",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.InMemoryConfigurationWrong"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "JSON Parser broken",
      "status": null
    },
    {
      "tag": "req mw_com_fta.LifeCycleIssuesElementPtr",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 488,
        "column": 20
      },
      "name": "mw_com_fta.LifeCycleIssuesElementPtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrWrongTarget"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Life-Cycle issues",
      "status": null
    },
    {
      "tag": "req mw_com_fta.LifeCycleIssuesSamplePtr",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 496,
        "column": 20
      },
      "name": "mw_com_fta.LifeCycleIssuesSamplePtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ReturnsWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Life-Cycle issues",
      "status": null
    },
    {
      "tag": "req mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 504,
        "column": 20
      },
      "name": "mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Literaly wrong number of slots reserved",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ManipulateReadData",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 512,
        "column": 20
      },
      "name": "mw_com_fta.ManipulateReadData",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.InMemoryConfigurationWrong"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Manipulate read data",
      "status": null
    },
    {
      "tag": "req mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 520,
        "column": 20
      },
      "name": "mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Mapping from actual EventID to Event-Type incorrect",
      "status": null
    },
    {
      "tag": "req mw_com_fta.MessagePassingCorruptsTheMaxSampleValue",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 528,
        "column": 20
      },
      "name": "mw_com_fta.MessagePassingCorruptsTheMaxSampleValue",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SubscribeWithWrongMaxSampleCount"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Message passing corrupts the max. sample value",
      "status": null
    },
    {
      "tag": "req mw_com_fta.MethodIdCorrupted",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 536,
        "column": 20
      },
      "name": "mw_com_fta.MethodIdCorrupted",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodCalled"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "MethodId corrupted",
      "status": null
    },
    {
      "tag": "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 544,
        "column": 20
      },
      "name": "mw_com_fta.MiddlewareProvidedTypeIsWrong",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Middleware provided type is wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 552,
        "column": 20
      },
      "name": "mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "More than one SampleAllocateePtr in parallel",
      "status": null
    },
    {
      "tag": "req mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 560,
        "column": 20
      },
      "name": "mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Necessary size calculation retreives wrong value",
      "status": null
    },
    {
      "tag": "req mw_com_fta.NoUnmapOnDestruction",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 568,
        "column": 20
      },
      "name": "mw_com_fta.NoUnmapOnDestruction",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.NoResourcesFreed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "No unmap on destruction",
      "status": null
    },
    {
      "tag": "req mw_com_fta.NotAllEventsArePopulated",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 576,
        "column": 20
      },
      "name": "mw_com_fta.NotAllEventsArePopulated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOnlyPartiallyOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Not all events are populated",
      "status": null
    },
    {
      "tag": "req mw_com_fta.NotCreatedAtAll",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 584,
        "column": 20
      },
      "name": "mw_com_fta.NotCreatedAtAll",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Not created at all",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OfferCallDidNotCheckIfUserProvidedFieldValues",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 592,
        "column": 20
      },
      "name": "mw_com_fta.OfferCallDidNotCheckIfUserProvidedFieldValues",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedWithoutInitialFieldValue"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Offer call did not check, if user provided field values",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OfferStateInconsistent",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 600,
        "column": 20
      },
      "name": "mw_com_fta.OfferStateInconsistent",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferInconsistent"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Offer State inconsistent",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OffsetPtrCorruption",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 608,
        "column": 20
      },
      "name": "mw_com_fta.OffsetPtrCorruption",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Offset PTR corruption",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OmitReadingOfRelevantElements",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 616,
        "column": 20
      },
      "name": "mw_com_fta.OmitReadingOfRelevantElements",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.InMemoryConfigurationWrong"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Omit reading of relevant elements",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OrderingWrong",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 624,
        "column": 20
      },
      "name": "mw_com_fta.OrderingWrong",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Ordering wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OsCreatesFileWithWrongName",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 632,
        "column": 20
      },
      "name": "mw_com_fta.OsCreatesFileWithWrongName",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceOfferedUnderWrongIds"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "OS creates file with wrong name",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OsRelatedFunctionalityFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 640,
        "column": 20
      },
      "name": "mw_com_fta.OsRelatedFunctionalityFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "OS related functionality failed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.OverwriteOfElementInUse",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 648,
        "column": 20
      },
      "name": "mw_com_fta.OverwriteOfElementInUse",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrFailsToFree"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Overwrite of element in use",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ProxyCrashesWithoutUnsubscription",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 656,
        "column": 20
      },
      "name": "mw_com_fta.ProxyCrashesWithoutUnsubscription",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.DoesNotUnsubscribe"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Proxy crashes without unsubscription",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ProxyIdOverwritten",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 664,
        "column": 20
      },
      "name": "mw_com_fta.ProxyIdOverwritten",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Proxy ID overwritten",
      "status": null
    },
    {
      "tag": "req mw_com_fta.PtrDangling",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 672,
        "column": 20
      },
      "name": "mw_com_fta.PtrDangling",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "PTR dangling",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ReceiveErrorOnRegistration",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 680,
        "column": 20
      },
      "name": "mw_com_fta.ReceiveErrorOnRegistration",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventOnlyPartiallyNotifiesConsumer"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Receive error on registration",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ReferencesInvalidMemory",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 688,
        "column": 20
      },
      "name": "mw_com_fta.ReferencesInvalidMemory",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrWrongTarget"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "References invalid memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ReferencesValidMemoryInsideSHM",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 696,
        "column": 20
      },
      "name": "mw_com_fta.ReferencesValidMemoryInsideSHM",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrWrongTarget"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "References valid memory inside shared-memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ReferencesValidMemoryOutsideSHM",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 704,
        "column": 20
      },
      "name": "mw_com_fta.ReferencesValidMemoryOutsideSHM",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MethodSignatureElementPtrWrongTarget"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "References valid memory outside shared-memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.RetryLogicNotBulletProof",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 712,
        "column": 20
      },
      "name": "mw_com_fta.RetryLogicNotBulletProof",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Retry-logic not bullet proof",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDClientMarkerFileNotFound",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 720,
        "column": 20
      },
      "name": "mw_com_fta.SDClientMarkerFileNotFound",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferNotStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Marker File Not found",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDClientMarkerFileWrongPath",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 728,
        "column": 20
      },
      "name": "mw_com_fta.SDClientMarkerFileWrongPath",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferNotStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Marker File Wrong path",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDClientWrongMarkerFile",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 736,
        "column": 20
      },
      "name": "mw_com_fta.SDClientWrongMarkerFile",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferWrongInstanceStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service Discovery Client deletes wrong marker file",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDFileDeletionFailure",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 744,
        "column": 20
      },
      "name": "mw_com_fta.SDFileDeletionFailure",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferNotStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Marker File Deletion Failure",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDNotifyFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 752,
        "column": 20
      },
      "name": "mw_com_fta.SDNotifyFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferNotStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "inotify Event Failure",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SDNotifyWrongFD",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 760,
        "column": 20
      },
      "name": "mw_com_fta.SDNotifyWrongFD",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferWrongInstanceStoppedInSD"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "inotify notifies wrong FD",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SHMObjectWrongPath",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 768,
        "column": 20
      },
      "name": "mw_com_fta.SHMObjectWrongPath",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferUnlinkWrongSHMObjects"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong SHM path created",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServerProcessCrash",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 776,
        "column": 20
      },
      "name": "mw_com_fta.ServerProcessCrash",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventOnlyPartiallyNotifiesConsumer"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Server process crash",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceInstanceUsageLockMechanismFailed",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 784,
        "column": 20
      },
      "name": "mw_com_fta.ServiceInstanceUsageLockMechanismFailed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferUnlinkWrongSHMObjects"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service instance usage lock mechanism failed",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceInstanceUsageNotChecked",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 792,
        "column": 20
      },
      "name": "mw_com_fta.ServiceInstanceUsageNotChecked",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StopOfferUnlinkWrongSHMObjects"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service instance usage not checked",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceWasAlreadyOfferedByOurProcess",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 800,
        "column": 20
      },
      "name": "mw_com_fta.ServiceWasAlreadyOfferedByOurProcess",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.OffersAlreadyOfferedService"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service was already offered by our process",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceWasAlreadyOfferedByPreviousDiedProcess",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 808,
        "column": 20
      },
      "name": "mw_com_fta.ServiceWasAlreadyOfferedByPreviousDiedProcess",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.OffersAlreadyOfferedService"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service was already offered by previous died process",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceWasOfferedButNotUnlikedOnStopOffer",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 816,
        "column": 20
      },
      "name": "mw_com_fta.ServiceWasOfferedButNotUnlikedOnStopOffer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service was offered, but not unliked on stop offer",
      "status": null
    },
    {
      "tag": "req mw_com_fta.ServiceWasOfferedByAnotherProcess",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 824,
        "column": 20
      },
      "name": "mw_com_fta.ServiceWasOfferedByAnotherProcess",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.OffersAlreadyOfferedService"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Service was offered by another process",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryIsOpenedEventhoughFileDoesNotExist",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 832,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryIsOpenedEventhoughFileDoesNotExist",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory is opened eventhough file does not exist",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryObjectDoesNotExist",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 840,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryObjectDoesNotExist",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory Object does not exist",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 848,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared memory Resource opens wrong shared memory segment",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 856,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory resource returns wrong proxy",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryRessourceNotForwarded",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 864,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryRessourceNotForwarded",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory ressource not forwarded",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemorySegmentDoesNotTryToCreateSegment",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 872,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemorySegmentDoesNotTryToCreateSegment",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory segment does not try to create segment.",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemorySegmentIsNotUnlinked",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 880,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemorySegmentIsNotUnlinked",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.NoResourcesFreed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory segment is not unlinked",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemorySegmentsAreCreatedUnderWrongName",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 888,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemorySegmentsAreCreatedUnderWrongName",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared Memory segments are created under wrong name",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedMemoryTruncationFails",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 896,
        "column": 20
      },
      "name": "mw_com_fta.SharedMemoryTruncationFails",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TooFewMemoryAllocated"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Shared memory truncation fails",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 904,
        "column": 20
      },
      "name": "mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "SharedMemoryFactory returns wrong memory ressource",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SizeWasManipulatedInSharedMemory",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 912,
        "column": 20
      },
      "name": "mw_com_fta.SizeWasManipulatedInSharedMemory",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TheSizeReturnedIsBiggerThenTheActualValue"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Size was manipulated in Shared Memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SizeWasWronglySetInSharedMemory",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 920,
        "column": 20
      },
      "name": "mw_com_fta.SizeWasWronglySetInSharedMemory",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.TheSizeReturnedIsBiggerThenTheActualValue"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Size was wrongly set in Shared Memory",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SlotAllocationSynchronisationWrongState",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 928,
        "column": 20
      },
      "name": "mw_com_fta.SlotAllocationSynchronisationWrongState",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Slot allocation synchronisation wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 936,
        "column": 20
      },
      "name": "mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackInvokedWithWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Slot allocation synchronisation wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.SlotReferenceBrokenEGNonValid",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 944,
        "column": 20
      },
      "name": "mw_com_fta.SlotReferenceBrokenEGNonValid",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.DoesNotFreeResourcesOnDestruction"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Slot reference broken e.g. non-valid",
      "status": null
    },
    {
      "tag": "req mw_com_fta.StaticCreateFunctionReturnsAnError",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 952,
        "column": 20
      },
      "name": "mw_com_fta.StaticCreateFunctionReturnsAnError",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CreationOfSkeletonNotPossible"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Static create function returns an error",
      "status": null
    },
    {
      "tag": "req mw_com_fta.UserFehler",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 960,
        "column": 20
      },
      "name": "mw_com_fta.UserFehler",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "User Fehler",
      "status": null
    },
    {
      "tag": "req mw_com_fta.UserMethodCallHandlerAssignmentWrong",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 968,
        "column": 20
      },
      "name": "mw_com_fta.UserMethodCallHandlerAssignmentWrong",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongMethodCalled"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "User Handler assignment wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.UserProvidedTypeIsWrong",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 976,
        "column": 20
      },
      "name": "mw_com_fta.UserProvidedTypeIsWrong",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.MemoryAllocatedInWrongSection"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "User provided type is wrong",
      "status": null
    },
    {
      "tag": "req mw_com_fta.UserProvidedWrongConfiguration",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 984,
        "column": 20
      },
      "name": "mw_com_fta.UserProvidedWrongConfiguration",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.InMemoryConfigurationWrong"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "User provided wrong configuration",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WatchesAreSetWrongly",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 992,
        "column": 20
      },
      "name": "mw_com_fta.WatchesAreSetWrongly",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.StartFindServiceCallbackCalledUnexpectedly"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Watches are set wrongly",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WritingStateChangeIsNotWorking",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1000,
        "column": 20
      },
      "name": "mw_com_fta.WritingStateChangeIsNotWorking",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SendingEventDoesNotFreeResources"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Writing State change is not working",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongAcl",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1008,
        "column": 20
      },
      "name": "mw_com_fta.WrongAcl",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong ACL",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongAclConfigurationForShmSegments",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1016,
        "column": 20
      },
      "name": "mw_com_fta.WrongAclConfigurationForShmSegments",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackNotInvokedDespiteSamplesAvailable"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong ACL configuration for SHM segments",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongDirectoryStructure",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1024,
        "column": 20
      },
      "name": "mw_com_fta.WrongDirectoryStructure",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong Directory Structure",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongMarkerFileName",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1032,
        "column": 20
      },
      "name": "mw_com_fta.WrongMarkerFileName",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotOffered"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong Marker File name",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongMemoryResourceProxy",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1040,
        "column": 20
      },
      "name": "mw_com_fta.WrongMemoryResourceProxy",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResourcesFreed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong memory resource proxy",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongName",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1048,
        "column": 20
      },
      "name": "mw_com_fta.WrongName",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong Name",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongNameOfSharedMemorySegment",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1056,
        "column": 20
      },
      "name": "mw_com_fta.WrongNameOfSharedMemorySegment",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongResourcesFreed"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong name of shared memory segment",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongPathResolvedFromInstanceidentifier",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1064,
        "column": 20
      },
      "name": "mw_com_fta.WrongPathResolvedFromInstanceidentifier",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.WrongServiceFound"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong path resolved from InstanceIdentifier",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongProvider",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1072,
        "column": 20
      },
      "name": "mw_com_fta.WrongProvider",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceIsFoundButDoesNotExist"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong Provider",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongServiceDiscoveryMarkerFileSearchedFor",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1080,
        "column": 20
      },
      "name": "mw_com_fta.WrongServiceDiscoveryMarkerFileSearchedFor",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ServiceNotFound"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong service discovery marker file searched for",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongSlotReferenced",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1088,
        "column": 20
      },
      "name": "mw_com_fta.WrongSlotReferenced",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.ReturnsWrongData"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong slot referenced",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongValueInsertedSlotStatus",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1096,
        "column": 20
      },
      "name": "mw_com_fta.WrongValueInsertedSlotStatus",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackNotInvokedDespiteSamplesAvailable"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong value inserted",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongValueInsertedTimestamp",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1104,
        "column": 20
      },
      "name": "mw_com_fta.WrongValueInsertedTimestamp",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.CallbackNotInvokedDespiteSamplesAvailable"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong value inserted",
      "status": null
    },
    {
      "tag": "req mw_com_fta.WrongValueIsPassedToMessagePassingLibrary",
      "location": {
        "kind": "file",
        "file": "bazel-out/k8-fastbuild/bin/score/mw/com/dependability/safety_analysis/mw_com_safety_analysis/fta_events.trlc",
        "line": 1112,
        "column": 20
      },
      "name": "mw_com_fta.WrongValueIsPassedToMessagePassingLibrary",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req Communication.SubscribeWithWrongMaxSampleCount"
      ],
      "framework": "TRLC",
      "kind": "RootCause",
      "text": "Wrong value is passed to message passing library",
      "status": null
    }
  ],
  "generator": "lobster-trlc",
  "schema": "lobster-req-trace",
  "version": 4
}
