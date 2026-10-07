{
  "data": [
    {
      "tag": "req Communication.MonotonicSemiDynamicMemoryAllocation@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 19,
        "column": 14
      },
      "name": "Communication.MonotonicSemiDynamicMemoryAllocation",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that enough memory is configured for shared memory instances, in order that LoLa can perform all necessary allocations (e.g. push-back on a Vector).",
      "status": null
    },
    {
      "tag": "req Communication.CorrectlyConfiguredMaximumNumberOfSubscriber@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 28,
        "column": 14
      },
      "name": "Communication.CorrectlyConfiguredMaximumNumberOfSubscriber",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.UserProvidedWrongConfiguration",
        "req mw_com_fta.FileCorrupted",
        "req mw_com_fta.JsonParserBroken",
        "req mw_com_fta.ManipulateReadData",
        "req mw_com_fta.OmitReadingOfRelevantElements",
        "req mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
        "req mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
        "req mw_com_fta.HoldsMoreSampleptrThanAnnounced",
        "req mw_com_fta.HoldsMoreSampleptrThanConfigured",
        "req mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
        "req mw_com_fta.RetryLogicNotBulletProof",
        "req mw_com_fta.IssueInLockFreeSychronization",
        "req mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
        "req mw_com_fta.AllocateClaimsToFewMemory",
        "req mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
        "req mw_com_fta.SharedMemoryTruncationFails"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that correct maximum number of subscriber is configured for each event for each service instance.",
      "status": null
    },
    {
      "tag": "req Communication.CorrectlyConfiguredMaximumNumberOfMaximumElementsPerSubscriber@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 55,
        "column": 14
      },
      "name": "Communication.CorrectlyConfiguredMaximumNumberOfMaximumElementsPerSubscriber",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.UserProvidedWrongConfiguration",
        "req mw_com_fta.FileCorrupted",
        "req mw_com_fta.JsonParserBroken",
        "req mw_com_fta.ManipulateReadData",
        "req mw_com_fta.OmitReadingOfRelevantElements",
        "req mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
        "req mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
        "req mw_com_fta.HoldsMoreSampleptrThanAnnounced",
        "req mw_com_fta.HoldsMoreSampleptrThanConfigured",
        "req mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
        "req mw_com_fta.RetryLogicNotBulletProof",
        "req mw_com_fta.IssueInLockFreeSychronization",
        "req mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
        "req mw_com_fta.AllocateClaimsToFewMemory",
        "req mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
        "req mw_com_fta.SharedMemoryTruncationFails"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that correct maximum number of elements per subscriber is configured for each event for each service instance.",
      "status": null
    },
    {
      "tag": "req Communication.CorrectlyConfiguredAsilLevel@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 82,
        "column": 14
      },
      "name": "Communication.CorrectlyConfiguredAsilLevel",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.UserProvidedWrongConfiguration",
        "req mw_com_fta.FileCorrupted",
        "req mw_com_fta.JsonParserBroken",
        "req mw_com_fta.ManipulateReadData",
        "req mw_com_fta.OmitReadingOfRelevantElements"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that the ASIL Level on process level and per service instance is correctly configured.",
      "status": null
    },
    {
      "tag": "req Communication.OnlyLoLaSupportedTypes@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 98,
        "column": 14
      },
      "name": "Communication.OnlyLoLaSupportedTypes",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
        "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
        "req mw_com_fta.SharedMemoryRessourceNotForwarded",
        "req mw_com_fta.UserFehler",
        "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
        "req mw_com_fta.UserProvidedTypeIsWrong",
        "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
        "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
        "req mw_com_fta.OffsetPtrCorruption",
        "req mw_com_fta.BrokenAllocator",
        "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
        "req mw_com_fta.ProxyIdOverwritten"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that only types that are supported by LoLa are transmitted.",
      "status": null
    },
    {
      "tag": "req Communication.NoApisFromImplementationNamespace@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 121,
        "column": 14
      },
      "name": "Communication.NoApisFromImplementationNamespace",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that no API calls from the implementation namespace (e.g `impl`) are directly invoked or types from within are directly used.",
      "status": null
    },
    {
      "tag": "req Communication.NoGuaranteesForNotifications@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 130,
        "column": 14
      },
      "name": "Communication.NoGuaranteesForNotifications",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.ReceiveErrorOnRegistration",
        "req mw_com_fta.ServerProcessCrash",
        "req mw_com_fta.AlgorithmicBug"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that a miss behavior of event notification will not harm a safety goal.",
      "status": null
    },
    {
      "tag": "req Communication.CheckingForPossibleMessageOverflow@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 144,
        "column": 14
      },
      "name": "Communication.CheckingForPossibleMessageOverflow",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.PtrDangling",
        "req mw_com_fta.CallbackDangling",
        "req mw_com_fta.ActivelyManipulateByProgrammParts",
        "req mw_com_fta.EventfqidWronglyConstructed",
        "req mw_com_fta.OrderingWrong",
        "req mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
        "req mw_com_fta.SlotAllocationSynchronisationWrongState"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that a message overflow, which results in message loss will not harm a safety goal. If this is not possible, a check for message overflow and necessary actions need to be performed.",
      "status": null
    },
    {
      "tag": "req Communication.DifferentUserForAsilAndQmProcesses@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 162,
        "column": 14
      },
      "name": "Communication.DifferentUserForAsilAndQmProcesses",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.WrongValueInsertedSlotStatus",
        "req mw_com_fta.WrongAclConfigurationForShmSegments",
        "req mw_com_fta.WrongValueInsertedTimestamp",
        "req mw_com_fta.CallbackIsNotStoredCorrectly"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that processes with a different ASIL shall be executed within different user-ids.",
      "status": null
    },
    {
      "tag": "req Communication.ConfigOnASafeFilesystem@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 177,
        "column": 14
      },
      "name": "Communication.ConfigOnASafeFilesystem",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.UserProvidedWrongConfiguration",
        "req mw_com_fta.FileCorrupted",
        "req mw_com_fta.JsonParserBroken",
        "req mw_com_fta.ManipulateReadData",
        "req mw_com_fta.OmitReadingOfRelevantElements"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that any configuration item that is read at runtime by LoLa is stored on a safety certified filesystem (according to the highest supported safety level).",
      "status": null
    },
    {
      "tag": "req Communication.NoStaticContextSupport@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 193,
        "column": 14
      },
      "name": "Communication.NoStaticContextSupport",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that LoLa is not used within static context within C++.",
      "status": null
    },
    {
      "tag": "req Communication.NoGuaranteeInAvailabilityOfServices@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 202,
        "column": 14
      },
      "name": "Communication.NoGuaranteeInAvailabilityOfServices",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.StaticCreateFunctionReturnsAnError",
        "req mw_com_fta.InstanceSpecifierResolutionLogicBroken"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that no safety goal is harmed, because a service instance is not found.",
      "status": null
    },
    {
      "tag": "req Communication.NoNotificationOnTerminationOfProducer@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 215,
        "column": 14
      },
      "name": "Communication.NoNotificationOnTerminationOfProducer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that termination (either gracefully or due to a malfunction) of a producer will not lead to a violation of a safety goal.",
      "status": null
    },
    {
      "tag": "req Communication.CheckForNullptrOnAllocate@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 224,
        "column": 14
      },
      "name": "Communication.CheckForNullptrOnAllocate",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
        "req mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
        "req mw_com_fta.HoldsMoreSampleptrThanAnnounced",
        "req mw_com_fta.HoldsMoreSampleptrThanConfigured",
        "req mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
        "req mw_com_fta.RetryLogicNotBulletProof",
        "req mw_com_fta.IssueInLockFreeSychronization",
        "req mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
        "req mw_com_fta.AllocateClaimsToFewMemory",
        "req mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
        "req mw_com_fta.SharedMemoryTruncationFails"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be checked if Allocate() on an event will return a nullptr. If a nullptr is returned, the system shall transition to safe state.",
      "status": null
    },
    {
      "tag": "req Communication.OneProducerOnlyOneAllocateePtr@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 246,
        "column": 14
      },
      "name": "Communication.OneProducerOnlyOneAllocateePtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.MappingFromActualEventidToEventTypeIncorrect",
        "req mw_com_fta.LiteralyWrongNumberOfSlotsReserved",
        "req mw_com_fta.HoldsMoreSampleptrThanAnnounced",
        "req mw_com_fta.HoldsMoreSampleptrThanConfigured",
        "req mw_com_fta.ConsumerUsesAnOlderSlotThanHeAlreadyHasBlockedInThePreviousAccess",
        "req mw_com_fta.RetryLogicNotBulletProof",
        "req mw_com_fta.IssueInLockFreeSychronization",
        "req mw_com_fta.MoreThanOneSampleallocateeptrInParallel",
        "req mw_com_fta.AllocateClaimsToFewMemory",
        "req mw_com_fta.NecessarySizeCalculationRetreivesWrongValue",
        "req mw_com_fta.SharedMemoryTruncationFails"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that at any time a producer instance per event only holds one AllocateePtr.",
      "status": null
    },
    {
      "tag": "req Communication.NoCopySendWhileHoldingAllocateePtr@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 268,
        "column": 14
      },
      "name": "Communication.NoCopySendWhileHoldingAllocateePtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that Send(const& value) is not invoked while an AllocateePtr is held.",
      "status": null
    },
    {
      "tag": "req Communication.NoneReentrantMethodsPerEventInstance@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 276,
        "column": 14
      },
      "name": "Communication.NoneReentrantMethodsPerEventInstance",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that any LoLa API that is bound to a specific event instance is not called in a reentrant manner.",
      "status": null
    },
    {
      "tag": "req Communication.SkeletonAliveWhileItsAllocateePtrBeingUsed@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 285,
        "column": 14
      },
      "name": "Communication.SkeletonAliveWhileItsAllocateePtrBeingUsed",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.LifeCycleIssuesSamplePtr",
        "req mw_com_fta.WrongSlotReferenced"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that a Skeleton instance is still alive while any AllocateePtr returned by it is used.",
      "status": null
    },
    {
      "tag": "req Communication.EventSubscriptionActiveWhileHoldingSamplePtr@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 298,
        "column": 14
      },
      "name": "Communication.EventSubscriptionActiveWhileHoldingSamplePtr",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.LifeCycleIssuesSamplePtr",
        "req mw_com_fta.WrongSlotReferenced",
        "req mw_com_fta.PtrDangling",
        "req mw_com_fta.CallbackDangling",
        "req mw_com_fta.ActivelyManipulateByProgrammParts",
        "req mw_com_fta.EventfqidWronglyConstructed",
        "req mw_com_fta.OrderingWrong",
        "req mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
        "req mw_com_fta.SlotAllocationSynchronisationWrongState"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that Unsubscribe() isn't called on a proxy event instance as long as any SamplePtr provided by it, is still held. Also the corresponding proxy instance shall be kept alive as on destruction it would implicitly call Unsubscribe().",
      "status": null
    },
    {
      "tag": "req Communication.NoneTerminatingCallbacks@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 318,
        "column": 14
      },
      "name": "Communication.NoneTerminatingCallbacks",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that any callback passed to LoLa for invocation is not throwing.",
      "status": null
    },
    {
      "tag": "req Communication.ValidCallbacksWhileProxyAlive@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 327,
        "column": 14
      },
      "name": "Communication.ValidCallbacksWhileProxyAlive",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.PtrDangling",
        "req mw_com_fta.CallbackDangling",
        "req mw_com_fta.ActivelyManipulateByProgrammParts",
        "req mw_com_fta.EventfqidWronglyConstructed",
        "req mw_com_fta.OrderingWrong",
        "req mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
        "req mw_com_fta.SlotAllocationSynchronisationWrongState"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that all callbacks passed towards LoLa are valid as long as the associated proxy is alive.",
      "status": null
    },
    {
      "tag": "req Communication.QualityOfDataIsDependentOnProducer@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 345,
        "column": 14
      },
      "name": "Communication.QualityOfDataIsDependentOnProducer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.PtrDangling",
        "req mw_com_fta.CallbackDangling",
        "req mw_com_fta.ActivelyManipulateByProgrammParts",
        "req mw_com_fta.EventfqidWronglyConstructed",
        "req mw_com_fta.OrderingWrong",
        "req mw_com_fta.SlotAllocationSynchronisationWrongTimestamp",
        "req mw_com_fta.SlotAllocationSynchronisationWrongState"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that the necessary quality of data is produced by the respective skeleton process.",
      "status": null
    },
    {
      "tag": "req Communication.ValidityOfPointerOnLoLaPointer@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 363,
        "column": 14
      },
      "name": "Communication.ValidityOfPointerOnLoLaPointer",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.LifeCycleIssuesSamplePtr",
        "req mw_com_fta.WrongSlotReferenced"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that no pointer, pointing to the memory of a SamplePtr or AllocateePtr is used once the SamplePtr or AllocateePtr are invalid.",
      "status": null
    },
    {
      "tag": "req Communication.LoLaMemoryOnlyAccessedThroughLoLa@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 376,
        "column": 14
      },
      "name": "Communication.LoLaMemoryOnlyAccessedThroughLoLa",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
        "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
        "req mw_com_fta.SharedMemoryRessourceNotForwarded",
        "req mw_com_fta.UserFehler",
        "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
        "req mw_com_fta.UserProvidedTypeIsWrong",
        "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
        "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
        "req mw_com_fta.OffsetPtrCorruption",
        "req mw_com_fta.BrokenAllocator",
        "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
        "req mw_com_fta.ProxyIdOverwritten"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that no other code accesses the mapped memory managed by LoLa.",
      "status": null
    },
    {
      "tag": "req Communication.NoSharedMemoryAllocationInNamespaceLola@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 399,
        "column": 14
      },
      "name": "Communication.NoSharedMemoryAllocationInNamespaceLola",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
        "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
        "req mw_com_fta.SharedMemoryRessourceNotForwarded",
        "req mw_com_fta.UserFehler",
        "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
        "req mw_com_fta.UserProvidedTypeIsWrong",
        "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
        "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
        "req mw_com_fta.OffsetPtrCorruption",
        "req mw_com_fta.BrokenAllocator",
        "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
        "req mw_com_fta.ProxyIdOverwritten"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that no other code creates shared memory segments beginning with \"lola\".",
      "status": null
    },
    {
      "tag": "req Communication.OnlyQnx71Supported@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 422,
        "column": 14
      },
      "name": "Communication.OnlyQnx71Supported",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
        "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
        "req mw_com_fta.SharedMemoryRessourceNotForwarded",
        "req mw_com_fta.UserFehler",
        "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
        "req mw_com_fta.UserProvidedTypeIsWrong",
        "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
        "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
        "req mw_com_fta.OffsetPtrCorruption",
        "req mw_com_fta.BrokenAllocator",
        "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
        "req mw_com_fta.ProxyIdOverwritten"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that any application containing LoLa is only executed on QNX Safe Operating System 7.1.",
      "status": null
    },
    {
      "tag": "req Communication.LoLaSpecificQnxMessagingEndPointsOnlyAccessedThroughLoLa@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 445,
        "column": 14
      },
      "name": "Communication.LoLaSpecificQnxMessagingEndPointsOnlyAccessedThroughLoLa",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.ReceiveErrorOnRegistration",
        "req mw_com_fta.ServerProcessCrash",
        "req mw_com_fta.AlgorithmicBug"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that the LoLa specific QNX Message Passing end-points are only accessed through LoLa APIs.",
      "status": null
    },
    {
      "tag": "req Communication.AragenNotSafe@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 459,
        "column": 14
      },
      "name": "Communication.AragenNotSafe",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "Input artifacts shall be manually reviewed for correctness",
      "status": null
    },
    {
      "tag": "req Communication.UnsupportedDataTypes@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 468,
        "column": 14
      },
      "name": "Communication.UnsupportedDataTypes",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.SharedMemoryResourceReturnsWrongProxy",
        "req mw_com_fta.SharedmemoryfactoryReturnsWrongMemoryRessource",
        "req mw_com_fta.SharedMemoryRessourceNotForwarded",
        "req mw_com_fta.UserFehler",
        "req mw_com_fta.MiddlewareProvidedTypeIsWrong",
        "req mw_com_fta.UserProvidedTypeIsWrong",
        "req mw_com_fta.SharedMemoryResourceOpensWrongSharedMemorySegment",
        "req mw_com_fta.ForwardedTheWrongSharedMemorySegmentFromTheBeginning",
        "req mw_com_fta.OffsetPtrCorruption",
        "req mw_com_fta.BrokenAllocator",
        "req mw_com_fta.DataTypeItselfIsAllocatedOnStack",
        "req mw_com_fta.ProxyIdOverwritten"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that neither variants nor maps are sent via LoLa.",
      "status": null
    },
    {
      "tag": "req Communication.NoGuaranteeOnExecutionTime@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 491,
        "column": 14
      },
      "name": "Communication.NoGuaranteeOnExecutionTime",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "There is no guarantee on the execution time of any function call provided by LoLa.",
      "status": null
    },
    {
      "tag": "req Communication.UsageOfConfigurationOversubscription@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 500,
        "column": 14
      },
      "name": "Communication.UsageOfConfigurationOversubscription",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "If event instance \"oversubscription\" is enabled, LoLa makes no warranty that proxies/consumers can't suffer from data loss! It is the responsibility of the user to adapt scheduling/event-data access in a way that no data-loss happens.",
      "status": null
    },
    {
      "tag": "req Communication.SameCompilerSettingsForProviderAndConsumerSide@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 508,
        "column": 14
      },
      "name": "Communication.SameCompilerSettingsForProviderAndConsumerSide",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "All compiler settings having influence on the binary representation of data exchanged via {{mw::com}}/{{LoLa}} (event, field, service-method payloads) have to be identical for compilation of code containing {{mw::com}} proxies and skeletons, which communicate.",
      "status": null
    },
    {
      "tag": "req Communication.EventOrFieldReceptionViaGenericProxyNeedsSpecificCare@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 515,
        "column": 14
      },
      "name": "Communication.EventOrFieldReceptionViaGenericProxyNeedsSpecificCare",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "When receiving event or field data via untyped {{GenericProxyEvent}} or {{GenericProxyField}}, care has to be taken when accessing the corresponding {{SamplePtr<void>}} delivered by calls to {{GetNewSamples()}}: When casting it to the expected type, it needs to be checked that no access behind the size returned by {{GetSampleSize()}} will happen.",
      "status": null
    },
    {
      "tag": "req Communication.CorrectlyConfiguredEventsFieldsPerServiceType@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 522,
        "column": 14
      },
      "name": "Communication.CorrectlyConfiguredEventsFieldsPerServiceType",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that all safety relevant events/fields in the service type are the same in all configurations.",
      "status": null
    },
    {
      "tag": "req Communication.NoGuaranteesForTimelyMethodCallExecution@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 531,
        "column": 14
      },
      "name": "Communication.NoGuaranteesForTimelyMethodCallExecution",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.BlocksOnCaller",
        "req mw_com_fta.CallBlocksOnCallee",
        "req mw_com_fta.CallBlocksOnUserHandler"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that a blocking method call will not harm a safety goal.",
      "status": null
    },
    {
      "tag": "req Communication.MethodInArgPtrMatches@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 545,
        "column": 14
      },
      "name": "Communication.MethodInArgPtrMatches",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "refs": [
        "req mw_com_fta.BlocksOnCaller",
        "req mw_com_fta.CallBlocksOnCallee",
        "req mw_com_fta.CallBlocksOnUserHandler"
      ],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "It shall be ensured that the memory locations of the method call in-arguments provided at the caller side are exactly the same as the memory locations as used at the callee side.",
      "status": null
    },
    {
      "tag": "req Communication.NoGuaranteeOnSubscriptionStateCorrectness@1",
      "location": {
        "kind": "file",
        "file": "score/mw/com/dependability/safety_analysis/aou.trlc",
        "line": 559,
        "column": 14
      },
      "name": "Communication.NoGuaranteeOnSubscriptionStateCorrectness",
      "messages": [],
      "just_up": [],
      "just_down": [],
      "just_global": [],
      "framework": "TRLC",
      "kind": "AoU",
      "text": "For safety critical use cases, an application must treat a SubscriptionState of kSubscribed or kSubscriptionPending (returned by GetSubscriptionState() or reported by the SubscriptionStateChangeHandler) as the same.",
      "status": null
    }
  ],
  "generator": "lobster-trlc",
  "schema": "lobster-req-trace",
  "version": 4
}
