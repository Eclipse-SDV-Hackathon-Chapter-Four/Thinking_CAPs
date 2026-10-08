{
  "data": [
    {
      "tag": "req Communication.AnyFunctionBlocksLongerThanExpected",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 20,
        "column": 26
      },
      "name": "Communication.AnyFunctionBlocksLongerThanExpected",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Any API of mw::com (LoLa) blocks longer than expected (or indefinite)",
      "status": null
    },
    {
      "tag": "req Communication.InMemoryConfigurationWrong",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 31,
        "column": 26
      },
      "name": "Communication.InMemoryConfigurationWrong",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Runtime.Initialize"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The in-memory (cpp representation) does not match the on file-system JSON configuration.",
      "status": null
    },
    {
      "tag": "req Communication.FunctionCalledFromMultipleThreads",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 42,
        "column": 26
      },
      "name": "Communication.FunctionCalledFromMultipleThreads",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Any API is called within multiple threads concurrently without any further synchronization.",
      "status": null
    },
    {
      "tag": "req Communication.GeneratedCodeDoesNotMatchGenerationInputs",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 53,
        "column": 26
      },
      "name": "Communication.GeneratedCodeDoesNotMatchGenerationInputs",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Proxys and Skeletons as data-types are generated using the aragen and not handwritten, may not match to the input (Meta-Model).",
      "status": null
    },
    {
      "tag": "req Communication.MisusedApis",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 64,
        "column": 26
      },
      "name": "Communication.MisusedApis",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "APIs are invoked in either an invalid context or non public APIs are invoked.",
      "status": null
    },
    {
      "tag": "req Communication.CreationOfSkeletonNotPossible",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 79,
        "column": 34
      },
      "name": "Communication.CreationOfSkeletonNotPossible",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.Create"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "It is not possible to create a skeleton instance",
      "status": null
    },
    {
      "tag": "req Communication.ServiceOfferedWithoutInitialFieldValue",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 93,
        "column": 34
      },
      "name": "Communication.ServiceOfferedWithoutInitialFieldValue",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A service is offered, although at least one of its field has no initial value set by the provider.",
      "status": null
    },
    {
      "tag": "req Communication.ServiceNotOffered",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 104,
        "column": 34
      },
      "name": "Communication.ServiceNotOffered",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A skeleton service is offering a service, but the service is silently not offered. Note: offered in this case means, that it is also connectable",
      "status": null
    },
    {
      "tag": "req Communication.ServiceOfferedOnWrongBinding",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 115,
        "column": 34
      },
      "name": "Communication.ServiceOfferedOnWrongBinding",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A skeleton is offering a service on the wrong binding. Meaning, the service is not offered on the intended binding, but on an unintended one.",
      "status": null
    },
    {
      "tag": "req Communication.ServiceOfferedUnderWrongIds",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 126,
        "column": 34
      },
      "name": "Communication.ServiceOfferedUnderWrongIds",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A skeleton is offering a service with wrong identifiers. This can include a service id, a instance id or also the service version.",
      "status": null
    },
    {
      "tag": "req Communication.OffersAlreadyOfferedService",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 137,
        "column": 34
      },
      "name": "Communication.OffersAlreadyOfferedService",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A skeleton offers a service that was already offered. Either by another process or by itself.",
      "status": null
    },
    {
      "tag": "req Communication.ServiceOnlyPartiallyOffered",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 148,
        "column": 34
      },
      "name": "Communication.ServiceOnlyPartiallyOffered",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.OfferService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A skeleton offers a service, which is not visible to all consumers, but only to parts of them.",
      "status": null
    },
    {
      "tag": "req Communication.StopOfferNotStoppedInSD",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 160,
        "column": 34
      },
      "name": "Communication.StopOfferNotStoppedInSD",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A service instance was offered via service discovery, but it wasn't withdrawn from service discovery in the stop offer.",
      "status": null
    },
    {
      "tag": "req Communication.StopOfferWrongInstanceStoppedInSD",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 169,
        "column": 34
      },
      "name": "Communication.StopOfferWrongInstanceStoppedInSD",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Same as in StopOfferNotStoppedInSD. Additionally another service instance, which is still being offered, is withdrawn from service discovery.",
      "status": null
    },
    {
      "tag": "req Communication.StopOfferUnlinkWrongSHMObjects",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 178,
        "column": 34
      },
      "name": "Communication.StopOfferUnlinkWrongSHMObjects",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Skeleton instance did unlink shared memory objects which do not belong to the service instance being stop offered.",
      "status": null
    },
    {
      "tag": "req Communication.StopOfferInconsistent",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 187,
        "column": 34
      },
      "name": "Communication.StopOfferInconsistent",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Skeleton instance is in an inconsistent state after stop offering: Either the stop offer was not forwarded to the binding or failed at the binding. Or it wasn't forwarded to the dependent service elements or their bindings or failed at them.",
      "status": null
    },
    {
      "tag": "req Communication.MemoryAllocatedInWrongSection",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 200,
        "column": 34
      },
      "name": "Communication.MemoryAllocatedInWrongSection",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The memory for an event is allocated in the wrong memory section (e.g. in Heap, another Shared Memory segment or the stack).",
      "status": null
    },
    {
      "tag": "req Communication.TooFewMemoryAllocated",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 210,
        "column": 34
      },
      "name": "Communication.TooFewMemoryAllocated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.Allocate"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The event allocation allocates too few memory (including no memory at all).",
      "status": null
    },
    {
      "tag": "req Communication.WronglyAlignedMemoryAllocated",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 221,
        "column": 34
      },
      "name": "Communication.WronglyAlignedMemoryAllocated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The memory for an event/field is allocated in a wrongly aligned manner.",
      "status": null
    },
    {
      "tag": "req Communication.TooMuchMemoryAllocated",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 232,
        "column": 34
      },
      "name": "Communication.TooMuchMemoryAllocated",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "There is too much memory allocated for one event/field",
      "status": null
    },
    {
      "tag": "req Communication.AllocatesAlreadyAllocatedMemory",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 243,
        "column": 34
      },
      "name": "Communication.AllocatesAlreadyAllocatedMemory",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The memory for an event/field is allocated from already allocated memory (not free memory).",
      "status": null
    },
    {
      "tag": "req Communication.SendingEventChangesUserData",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 257,
        "column": 34
      },
      "name": "Communication.SendingEventChangesUserData",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.Send"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A call to send manipulates the data that was provided by the caller.",
      "status": null
    },
    {
      "tag": "req Communication.SendingAnEventOrFieldSendsDataOnlyPartially",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 268,
        "column": 34
      },
      "name": "Communication.SendingAnEventOrFieldSendsDataOnlyPartially",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Data that is send by the user, only reaches partially the consumer. This can happen in two ways, only a partial number of consumers see the data or all consumers see only partial data.",
      "status": null
    },
    {
      "tag": "req Communication.SendingEventOnlyPartiallyNotifiesConsumer",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 279,
        "column": 34
      },
      "name": "Communication.SendingEventOnlyPartiallyNotifiesConsumer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.Send"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "When data is sent, consumers that have a callback registered, are only partially notified.",
      "status": null
    },
    {
      "tag": "req Communication.SendingEventSendsToWrongConsumer",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 290,
        "column": 34
      },
      "name": "Communication.SendingEventSendsToWrongConsumer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.Send"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "An event or field is sent to the wrong consumer.",
      "status": null
    },
    {
      "tag": "req Communication.SendingAnEventOrFieldSendsSameSampleNtimes",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 301,
        "column": 34
      },
      "name": "Communication.SendingAnEventOrFieldSendsSameSampleNtimes",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Instead of sending a sample (one data point) only once, it is send multiple times.",
      "status": null
    },
    {
      "tag": "req Communication.SendingEventDoesNotFreeResources",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 312,
        "column": 34
      },
      "name": "Communication.SendingEventDoesNotFreeResources",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.Send"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Resources in the middleware that have been allocated with a previous allocation, are not freed after returning from send/update.",
      "status": null
    },
    {
      "tag": "req Communication.WrongResourcesFreed",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 326,
        "column": 34
      },
      "name": "Communication.WrongResourcesFreed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.Destroy"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A destruction of one skeleton instances, frees the resources of another skeleton instance.",
      "status": null
    },
    {
      "tag": "req Communication.NoResourcesFreed",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 337,
        "column": 34
      },
      "name": "Communication.NoResourcesFreed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Skeleton.Destroy"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The resources allocated on construction and during operation are not freed on destruction.",
      "status": null
    },
    {
      "tag": "req Communication.EarlyCleanUp",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 348,
        "column": 34
      },
      "name": "Communication.EarlyCleanUp",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Resources are freed while still being used.",
      "status": null
    },
    {
      "tag": "req Communication.WrongMethodInArgsUsed",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 368,
        "column": 34
      },
      "name": "Communication.WrongMethodInArgsUsed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Unintended input arguments are used in a service method call. Therefore, the method call gets executed with wrong input data.",
      "status": null
    },
    {
      "tag": "req Communication.WrongMethodCalled",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 384,
        "column": 34
      },
      "name": "Communication.WrongMethodCalled",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Either the wrong user provided method handler is called or no user handler is called at all. Therefore, the method call results are invalid/garbage.",
      "status": null
    },
    {
      "tag": "req Communication.WrongResultsProvided",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 402,
        "column": 34
      },
      "name": "Communication.WrongResultsProvided",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The result of a method call is either not provided in the expected location, leaving uninitialized data in the expected location or it is provided in an inconsistent state. Therefore, the method call results are invalid/garbage.",
      "status": null
    },
    {
      "tag": "req Communication.StartFindServiceCallbackCalledUnexpectedly",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 418,
        "column": 34
      },
      "name": "Communication.StartFindServiceCallbackCalledUnexpectedly",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Proxy.StartFindService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The user-provided callback is invoked, even though it should not be invoked.",
      "status": null
    },
    {
      "tag": "req Communication.ServiceNotFound",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 432,
        "column": 34
      },
      "name": "Communication.ServiceNotFound",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Proxy.FindService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy does not find a service instance, even though it was offered by a skeleton.",
      "status": null
    },
    {
      "tag": "req Communication.WrongServiceFound",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 443,
        "column": 34
      },
      "name": "Communication.WrongServiceFound",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Proxy.FindService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy instance finds a wrong service. This could be either a wrong service instance or a completely wrong service.",
      "status": null
    },
    {
      "tag": "req Communication.ServiceIsFoundButDoesNotExist",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 457,
        "column": 34
      },
      "name": "Communication.ServiceIsFoundButDoesNotExist",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Proxy.FindService"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Finding a service, returns a service, even though no service instance was offered.",
      "status": null
    },
    {
      "tag": "req Communication.StartedFindServiceIsNotStopped",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 472,
        "column": 34
      },
      "name": "Communication.StartedFindServiceIsNotStopped",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A user called \"StartFindService\" with a given handler, and since \"StopFindService\" does not work, services can still be found.",
      "status": null
    },
    {
      "tag": "req Communication.WrongStartfindserviceIsStopped",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 483,
        "column": 34
      },
      "name": "Communication.WrongStartfindserviceIsStopped",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The handle provided to StopFindService, is identified as another one and thus stops the wrong service discovery query.",
      "status": null
    },
    {
      "tag": "req Communication.SubscribeToWrongEvent",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 497,
        "column": 34
      },
      "name": "Communication.SubscribeToWrongEvent",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A service proxy subscribes to a wrong event. This either means that this event does not exist at all, is offered by another service instance, another event in the current instance or a completely different service.",
      "status": null
    },
    {
      "tag": "req Communication.SubscribeWithWrongMaxSampleCount",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 507,
        "column": 34
      },
      "name": "Communication.SubscribeWithWrongMaxSampleCount",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy instance subscribes to an event to with a wrong sample count, meaning a different one that was provided by the user.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotSubscribe",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 517,
        "column": 34
      },
      "name": "Communication.DoesNotSubscribe",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy does not subscribe to a skeleton. Thus, a skeleton does not know that a proxy is interested in data.",
      "status": null
    },
    {
      "tag": "req Communication.ReceiveHandlerNotInvoked",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 531,
        "column": 34
      },
      "name": "Communication.ReceiveHandlerNotInvoked",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy has set a receive handler and a skeleton is updating an event, but the receive handler is never invoked.",
      "status": null
    },
    {
      "tag": "req Communication.ReceiveHandlerInvokedWithWrongEvent",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 542,
        "column": 34
      },
      "name": "Communication.ReceiveHandlerInvokedWithWrongEvent",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A receive handler registered for an event, gets called because of an update of an different event.",
      "status": null
    },
    {
      "tag": "req Communication.ReceiveHandlerInvokedMultipleTimes",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 552,
        "column": 34
      },
      "name": "Communication.ReceiveHandlerInvokedMultipleTimes",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A receive handler is invoked multiple times, even though only one event update happend.",
      "status": null
    },
    {
      "tag": "req Communication.ReceiveHandlerInvokedWithoutEventNotification",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 563,
        "column": 34
      },
      "name": "Communication.ReceiveHandlerInvokedWithoutEventNotification",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A receive handler is invoked, even though no event update happend.",
      "status": null
    },
    {
      "tag": "req Communication.CallbackNotInvokedDespiteSamplesAvailable",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 577,
        "column": 34
      },
      "name": "Communication.CallbackNotInvokedDespiteSamplesAvailable",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "GetNewSamples() gets called on an event with a callback F, but the callback gets called not at all, although at least one new sample is available.",
      "status": null
    },
    {
      "tag": "req Communication.CallbackInvokedWithWrongData",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 587,
        "column": 34
      },
      "name": "Communication.CallbackInvokedWithWrongData",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy receives a sample pointer via callback F(), but the data does not contain the expected one.",
      "status": null
    },
    {
      "tag": "req Communication.UsesToManySampleptr",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 597,
        "column": 34
      },
      "name": "Communication.UsesToManySampleptr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "User is already max. sample count SamplePtr, but we are still handing out SamplePtrs in callback F().",
      "status": null
    },
    {
      "tag": "req Communication.ReturnsWrongSampleCount",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 608,
        "column": 34
      },
      "name": "Communication.ReturnsWrongSampleCount",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Value returned by GetNewSample() does not match with the number of calls to callback F().",
      "status": null
    },
    {
      "tag": "req Communication.SucceedsDespiteAnError",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 619,
        "column": 34
      },
      "name": "Communication.SucceedsDespiteAnError",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.Event.GetNewSamples"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A user calls GetNewSamples() on a proxy instance and receives a sample count, even though he should have received an error.",
      "status": null
    },
    {
      "tag": "req Communication.ReturnsWrongFreeSampleCount",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 634,
        "column": 34
      },
      "name": "Communication.ReturnsWrongFreeSampleCount",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A user has already M SamplePtr in use from a max. announced number N, but GetFreeSampleCount() returns a different value than N-M.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotUnsubscribe",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 648,
        "column": 34
      },
      "name": "Communication.DoesNotUnsubscribe",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy is subscribed to an event, tries to unsubscribe, but silently fails to unsubscribe.",
      "status": null
    },
    {
      "tag": "req Communication.UnsubscribesFromWrongEvent",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 658,
        "column": 34
      },
      "name": "Communication.UnsubscribesFromWrongEvent",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A user unsubscribes from an event, but the unsubscribe is silently carried out on another event.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotImplicitRemoveReceiveHandler",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 669,
        "column": 34
      },
      "name": "Communication.DoesNotImplicitRemoveReceiveHandler",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A proxy has registered a receive handler and unsubscribes, this should lead to the case that a receive handler is no longer called. In this failure mode, the receive handler would still be called.",
      "status": null
    },
    {
      "tag": "req Communication.MapContainingNonexistentEvents",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 685,
        "column": 38
      },
      "name": "Communication.MapContainingNonexistentEvents",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The map that is visible to the user, contains events that are not actually existing (e.g. in the configuration).",
      "status": null
    },
    {
      "tag": "req Communication.IncompleteMapOfEvents",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 695,
        "column": 38
      },
      "name": "Communication.IncompleteMapOfEvents",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The user gets presented not all events the generic proxy supports.",
      "status": null
    },
    {
      "tag": "req Communication.TheSizeReturnedIsBiggerThenTheActualValue",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 709,
        "column": 38
      },
      "name": "Communication.TheSizeReturnedIsBiggerThenTheActualValue",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.GenericProxyEvent.GetSampleSize"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The user receives a size, that is bigger then the actual value.",
      "status": null
    },
    {
      "tag": "req Communication.TheSizeReturnedIsSmallerThenTheActualSize",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 720,
        "column": 38
      },
      "name": "Communication.TheSizeReturnedIsSmallerThenTheActualSize",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.GenericProxyEvent.GetSampleSize"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "The user receives a size, that is smaller then the actual value.",
      "status": null
    },
    {
      "tag": "req Communication.WrongIndicationIfFormatIsSerialized",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 732,
        "column": 38
      },
      "name": "Communication.WrongIndicationIfFormatIsSerialized",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw.com.GenericProxyEvent.HasSerializedFormat"
      ],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A user, using HasSerializedFormat(), receives the wrong value.",
      "status": null
    },
    {
      "tag": "req Communication.MethodCallBlocksLongerThanExpected",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 748,
        "column": 34
      },
      "name": "Communication.MethodCallBlocksLongerThanExpected",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A call to a service-method on the client/consumer side blocks longer than expected (or indefinite). This is a specific instance of FailureMode [AnyFunctionBlocksLongerThanExpected], but since with service-methods we have concrete root causes in the form of message-passing behaviour and behaviour of user-provided handler, we have this specific failure mode.",
      "status": null
    },
    {
      "tag": "req Communication.WrongMethodInArgsProvided",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 765,
        "column": 34
      },
      "name": "Communication.WrongMethodInArgsProvided",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Unintended input arguments are provided to a service method call. Therefore, the method call gets executed with wrong input data.",
      "status": null
    },
    {
      "tag": "req Communication.WrongReturnValueUsed",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 782,
        "column": 34
      },
      "name": "Communication.WrongReturnValueUsed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "Unintended results are provided from a service method call. Therefore, the caller of the method works on wrong data.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotFreeResourcesOnDestruction",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 802,
        "column": 34
      },
      "name": "Communication.DoesNotFreeResourcesOnDestruction",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A SampleAllocateePtr or SamplePtr is destroyed, which should lead to a freeing of resources, but caused by a fault they are not freed.",
      "status": null
    },
    {
      "tag": "req Communication.FreesWrongResources",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 812,
        "column": 34
      },
      "name": "Communication.FreesWrongResources",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A SampleAllocateePtr or SamplePtr free the wrong resources associated with them.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotReserveResources",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 823,
        "column": 34
      },
      "name": "Communication.DoesNotReserveResources",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "A SamplePtr or SampleAllocateePtr do not increase their respective ref-counts and thus avoid data changes.",
      "status": null
    },
    {
      "tag": "req Communication.DoesNotUpdateFreeSampleCountCorrectly",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 834,
        "column": 34
      },
      "name": "Communication.DoesNotUpdateFreeSampleCountCorrectly",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "When a SamplePtr gets created or destroyed for a given event instance, the Free Sample Count of this instance doesn't get updated accordingly",
      "status": null
    },
    {
      "tag": "req Communication.ReturnsWrongData",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 845,
        "column": 34
      },
      "name": "Communication.ReturnsWrongData",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "On dereferenciation of a SamplePtr or SampleAllocateePtr wrong data is returned.",
      "status": null
    },
    {
      "tag": "req Communication.MethodSignatureElementPtrWrongTarget",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 865,
        "column": 34
      },
      "name": "Communication.MethodSignatureElementPtrWrongTarget",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "On de-referencing of a MethodSignatureElementPtr wrong data is returned.",
      "status": null
    },
    {
      "tag": "req Communication.MethodSignatureElementPtrFailsToFree",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/failure_modes.trlc",
        "line": 880,
        "column": 34
      },
      "name": "Communication.MethodSignatureElementPtrFailsToFree",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "FailureMode",
      "text": "On destruction of a MethodSignatureElementPtr wrong memory is freed or not freed at all.",
      "status": null
    }
  ],
  "generator": "lobster-trlc",
  "schema": "lobster-req-trace",
  "version": 4
}
