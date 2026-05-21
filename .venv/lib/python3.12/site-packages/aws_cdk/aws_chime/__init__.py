r'''
# AWS::Chime Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_chime as chime
```

<!--BEGIN CFNONLY DISCLAIMER-->

There are no official hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet. Here are some suggestions on how to proceed:

* Search [Construct Hub for Chime construct libraries](https://constructs.dev/search?q=chime)
* Use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, in the same way you would use [the CloudFormation AWS::Chime resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_Chime.html) directly.

<!--BEGIN CFNONLY DISCLAIMER-->

There are no hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet.
However, you can still use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, and use this service exactly as you would using CloudFormation directly.

For more information on the resources and properties available for this service, see the [CloudFormation documentation for AWS::Chime](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_Chime.html).

(Read the [CDK Contributing Guide](https://github.com/aws/aws-cdk/blob/main/CONTRIBUTING.md) and submit an RFC if you are interested in contributing to this construct library.)

<!--END CFNONLY DISCLAIMER-->
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import constructs as _constructs_77d1e7e8
from .. import (
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    ITaggableV2 as _ITaggableV2_4e6798f8,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)
from ..interfaces.aws_chime import (
    AppInstanceBotReference as _AppInstanceBotReference_0e9addb1,
    AppInstanceReference as _AppInstanceReference_8414b2a0,
    IAppInstanceBotRef as _IAppInstanceBotRef_519ced67,
    IAppInstanceRef as _IAppInstanceRef_43d18bab,
)


@jsii.implements(_IInspectable_c2943556, _IAppInstanceRef_43d18bab, _ITaggableV2_4e6798f8)
class CfnAppInstance(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_chime.CfnAppInstance",
):
    '''Resource Type definition for AWS::Chime::AppInstance.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstance.html
    :cloudformationResource: AWS::Chime::AppInstance
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_chime as chime
        
        cfn_app_instance = chime.CfnAppInstance(self, "MyCfnAppInstance",
            name="name",
        
            # the properties below are optional
            metadata="metadata",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        name: builtins.str,
        metadata: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_CfnTag_f6864754", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::Chime::AppInstance``.

        :param scope: Scope in which this resource is defined.
        :param id: Construct identifier for this resource (unique in its scope).
        :param name: The name of the AppInstance.
        :param metadata: The metadata of the AppInstance. Limited to a 1KB string in UTF-8.
        :param tags: Tags assigned to the AppInstance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d337d6c149cc789c0b6f05ba4ba90f831464295606b004354b7815daaed0c77)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAppInstanceProps(name=name, metadata=metadata, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="arnForAppInstance")
    @builtins.classmethod
    def arn_for_app_instance(
        cls,
        resource: "_IAppInstanceRef_43d18bab",
    ) -> builtins.str:
        '''
        :param resource: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f74b0e7014ea5c23e28103a5fb5867813697fd8201279c330a3aa769bc126a1)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "arnForAppInstance", [resource]))

    @jsii.member(jsii_name="isCfnAppInstance")
    @builtins.classmethod
    def is_cfn_app_instance(cls, x: typing.Any) -> builtins.bool:
        '''Checks whether the given object is a CfnAppInstance.

        :param x: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a664656abafe2adc6e2a0a9db5e06dc33b5b3b6a0fa2a5ca0b61b7b95d0c32)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isCfnAppInstance", [x]))

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: "_TreeInspector_488e0dd5") -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__400a60274a57ac76d314b93fb263163beba6942cc730e90588d6f74e739f4eb0)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c4ccf5db0f869956272a9d89ee82b1cfb49e2aacbbc94b43a595151f8b37e60)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="appInstanceRef")
    def app_instance_ref(self) -> "_AppInstanceReference_8414b2a0":
        '''A reference to a AppInstance resource.'''
        return typing.cast("_AppInstanceReference_8414b2a0", jsii.get(self, "appInstanceRef"))

    @builtins.property
    @jsii.member(jsii_name="attrAppInstanceArn")
    def attr_app_instance_arn(self) -> builtins.str:
        '''The Amazon Resource Number (ARN) of the AppInstance.

        :cloudformationAttribute: AppInstanceArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAppInstanceArn"))

    @builtins.property
    @jsii.member(jsii_name="attrCreatedTimestamp")
    def attr_created_timestamp(self) -> "_IResolvable_da3f097b":
        '''The time at which an AppInstance was created.

        In epoch milliseconds.

        :cloudformationAttribute: CreatedTimestamp
        '''
        return typing.cast("_IResolvable_da3f097b", jsii.get(self, "attrCreatedTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="attrLastUpdatedTimestamp")
    def attr_last_updated_timestamp(self) -> "_IResolvable_da3f097b":
        '''The time an AppInstance was last updated.

        In epoch milliseconds.

        :cloudformationAttribute: LastUpdatedTimestamp
        '''
        return typing.cast("_IResolvable_da3f097b", jsii.get(self, "attrLastUpdatedTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="cdkTagManager")
    def cdk_tag_manager(self) -> "_TagManager_0a598cb3":
        '''Tag Manager which manages the tags for this resource.'''
        return typing.cast("_TagManager_0a598cb3", jsii.get(self, "cdkTagManager"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="cfnPropertyNames")
    def _cfn_property_names(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "cfnPropertyNames"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the AppInstance.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b72de3b84f85f89b400c53dced98e7828184761f13429f1028134b5727fe38e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the AppInstance.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4d28a89759474ddf9cf296e1da1bbf9afe7e7c1413d9a4d175db15deaca419f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["_CfnTag_f6864754"]]:
        '''Tags assigned to the AppInstance.'''
        return typing.cast(typing.Optional[typing.List["_CfnTag_f6864754"]], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["_CfnTag_f6864754"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc357af54a794ca273668787f93dac3a63d2f85c8108d86aa56926b60d6aac5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.implements(_IInspectable_c2943556, _IAppInstanceBotRef_519ced67, _ITaggableV2_4e6798f8)
class CfnAppInstanceBot(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceBot",
):
    '''Resource Type definition for AWS::Chime::AppInstanceBot.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html
    :cloudformationResource: AWS::Chime::AppInstanceBot
    :exampleMetadata: fixture=_generated

    Example::

        from aws_cdk import CfnTag
        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_chime as chime
        
        cfn_app_instance_bot = chime.CfnAppInstanceBot(self, "MyCfnAppInstanceBot",
            app_instance_arn="appInstanceArn",
            configuration=chime.CfnAppInstanceBot.ConfigurationProperty(
                lex=chime.CfnAppInstanceBot.LexConfigurationProperty(
                    lex_bot_alias_arn="lexBotAliasArn",
                    locale_id="localeId",
        
                    # the properties below are optional
                    invoked_by=chime.CfnAppInstanceBot.InvokedByProperty(
                        standard_messages="standardMessages",
                        targeted_messages="targetedMessages"
                    ),
                    responds_to="respondsTo",
                    welcome_intent="welcomeIntent"
                )
            ),
        
            # the properties below are optional
            metadata="metadata",
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        app_instance_arn: builtins.str,
        configuration: typing.Union["_IResolvable_da3f097b", typing.Union["CfnAppInstanceBot.ConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_CfnTag_f6864754", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::Chime::AppInstanceBot``.

        :param scope: Scope in which this resource is defined.
        :param id: Construct identifier for this resource (unique in its scope).
        :param app_instance_arn: The ARN of the AppInstance.
        :param configuration: A structure that contains configuration data.
        :param metadata: The metadata of the AppInstanceBot.
        :param name: The name of the AppInstanceBot.
        :param tags: The tags assigned to the AppInstanceBot.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca75944f6ceb69180d3b0f352517267777aeee7ffaa12b2f1a465cf9b6a3e00)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnAppInstanceBotProps(
            app_instance_arn=app_instance_arn,
            configuration=configuration,
            metadata=metadata,
            name=name,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="arnForAppInstanceBot")
    @builtins.classmethod
    def arn_for_app_instance_bot(
        cls,
        resource: "_IAppInstanceBotRef_519ced67",
    ) -> builtins.str:
        '''
        :param resource: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49c5faf3dcf2887594ff746db96b49d9757db79f86e9d6f358d9f275ee8c8210)
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "arnForAppInstanceBot", [resource]))

    @jsii.member(jsii_name="isCfnAppInstanceBot")
    @builtins.classmethod
    def is_cfn_app_instance_bot(cls, x: typing.Any) -> builtins.bool:
        '''Checks whether the given object is a CfnAppInstanceBot.

        :param x: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0255372b69a195b0351367c082f9533519223c17e242b93716f61ed8e55dea62)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isCfnAppInstanceBot", [x]))

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: "_TreeInspector_488e0dd5") -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427e24f474e9d78b560301eb631ab4ec523303c4565f63f29c83299fe5abafb1)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f31284f1d604da54c34b53acb2ff3863b786fb7370f15d19da68df814cd8ad)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="appInstanceBotRef")
    def app_instance_bot_ref(self) -> "_AppInstanceBotReference_0e9addb1":
        '''A reference to a AppInstanceBot resource.'''
        return typing.cast("_AppInstanceBotReference_0e9addb1", jsii.get(self, "appInstanceBotRef"))

    @builtins.property
    @jsii.member(jsii_name="attrAppInstanceBotArn")
    def attr_app_instance_bot_arn(self) -> builtins.str:
        '''The ARN of the AppInstanceBot.

        :cloudformationAttribute: AppInstanceBotArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrAppInstanceBotArn"))

    @builtins.property
    @jsii.member(jsii_name="attrCreatedTimestamp")
    def attr_created_timestamp(self) -> "_IResolvable_da3f097b":
        '''The time at which the AppInstanceBot was created.

        In epoch milliseconds.

        :cloudformationAttribute: CreatedTimestamp
        '''
        return typing.cast("_IResolvable_da3f097b", jsii.get(self, "attrCreatedTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="attrLastUpdatedTimestamp")
    def attr_last_updated_timestamp(self) -> "_IResolvable_da3f097b":
        '''The time at which the AppInstanceBot was last updated.

        In epoch milliseconds.

        :cloudformationAttribute: LastUpdatedTimestamp
        '''
        return typing.cast("_IResolvable_da3f097b", jsii.get(self, "attrLastUpdatedTimestamp"))

    @builtins.property
    @jsii.member(jsii_name="cdkTagManager")
    def cdk_tag_manager(self) -> "_TagManager_0a598cb3":
        '''Tag Manager which manages the tags for this resource.'''
        return typing.cast("_TagManager_0a598cb3", jsii.get(self, "cdkTagManager"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="cfnPropertyNames")
    def _cfn_property_names(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "cfnPropertyNames"))

    @builtins.property
    @jsii.member(jsii_name="appInstanceArn")
    def app_instance_arn(self) -> builtins.str:
        '''The ARN of the AppInstance.'''
        return typing.cast(builtins.str, jsii.get(self, "appInstanceArn"))

    @app_instance_arn.setter
    def app_instance_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13a53900f75f263ec868d4efe44340a9273169b155a8e54a68fe8cde3818baec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appInstanceArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(
        self,
    ) -> typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.ConfigurationProperty"]:
        '''A structure that contains configuration data.'''
        return typing.cast(typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.ConfigurationProperty"], jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(
        self,
        value: typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.ConfigurationProperty"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d36a14f99ec95cd590d6c1757bb41c8b9235cf6b317fa73e6692074ed033195a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the AppInstanceBot.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45024baca15a880d713b7458c08c15471a9b4b4bc485fcaa496535c2d75a30a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the AppInstanceBot.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ad6a83eab879d92eb2609e2f37735b3c2383bb2e7e24c6cefbec192e42c39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List["_CfnTag_f6864754"]]:
        '''The tags assigned to the AppInstanceBot.'''
        return typing.cast(typing.Optional[typing.List["_CfnTag_f6864754"]], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Optional[typing.List["_CfnTag_f6864754"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d87e45b7d9459784717058ca252a094c146e5656ea14d9da51f1cf05f4aa56d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceBot.ConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"lex": "lex"},
    )
    class ConfigurationProperty:
        def __init__(
            self,
            *,
            lex: typing.Union["_IResolvable_da3f097b", typing.Union["CfnAppInstanceBot.LexConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
        ) -> None:
            '''A structure that contains configuration data.

            :param lex: The configuration for an Amazon Lex V2 bot.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-configuration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_chime as chime
                
                configuration_property = chime.CfnAppInstanceBot.ConfigurationProperty(
                    lex=chime.CfnAppInstanceBot.LexConfigurationProperty(
                        lex_bot_alias_arn="lexBotAliasArn",
                        locale_id="localeId",
                
                        # the properties below are optional
                        invoked_by=chime.CfnAppInstanceBot.InvokedByProperty(
                            standard_messages="standardMessages",
                            targeted_messages="targetedMessages"
                        ),
                        responds_to="respondsTo",
                        welcome_intent="welcomeIntent"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__09ff343ee28319a719419e7819c467b339964da524abd8a8f50f44edd43b11a8)
                check_type(argname="argument lex", value=lex, expected_type=type_hints["lex"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "lex": lex,
            }

        @builtins.property
        def lex(
            self,
        ) -> typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.LexConfigurationProperty"]:
            '''The configuration for an Amazon Lex V2 bot.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-configuration.html#cfn-chime-appinstancebot-configuration-lex
            '''
            result = self._values.get("lex")
            assert result is not None, "Required property 'lex' is missing"
            return typing.cast(typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.LexConfigurationProperty"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceBot.InvokedByProperty",
        jsii_struct_bases=[],
        name_mapping={
            "standard_messages": "standardMessages",
            "targeted_messages": "targetedMessages",
        },
    )
    class InvokedByProperty:
        def __init__(
            self,
            *,
            standard_messages: builtins.str,
            targeted_messages: builtins.str,
        ) -> None:
            '''Specifies the type of message that triggers a bot.

            :param standard_messages: Sets standard messages as the bot trigger.
            :param targeted_messages: Sets targeted messages as the bot trigger.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-invokedby.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_chime as chime
                
                invoked_by_property = chime.CfnAppInstanceBot.InvokedByProperty(
                    standard_messages="standardMessages",
                    targeted_messages="targetedMessages"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e0a8291bb53d368f6b1012fdd17317226c377241787e7d74d9371e641c527be4)
                check_type(argname="argument standard_messages", value=standard_messages, expected_type=type_hints["standard_messages"])
                check_type(argname="argument targeted_messages", value=targeted_messages, expected_type=type_hints["targeted_messages"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "standard_messages": standard_messages,
                "targeted_messages": targeted_messages,
            }

        @builtins.property
        def standard_messages(self) -> builtins.str:
            '''Sets standard messages as the bot trigger.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-invokedby.html#cfn-chime-appinstancebot-invokedby-standardmessages
            '''
            result = self._values.get("standard_messages")
            assert result is not None, "Required property 'standard_messages' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def targeted_messages(self) -> builtins.str:
            '''Sets targeted messages as the bot trigger.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-invokedby.html#cfn-chime-appinstancebot-invokedby-targetedmessages
            '''
            result = self._values.get("targeted_messages")
            assert result is not None, "Required property 'targeted_messages' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InvokedByProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceBot.LexConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "lex_bot_alias_arn": "lexBotAliasArn",
            "locale_id": "localeId",
            "invoked_by": "invokedBy",
            "responds_to": "respondsTo",
            "welcome_intent": "welcomeIntent",
        },
    )
    class LexConfigurationProperty:
        def __init__(
            self,
            *,
            lex_bot_alias_arn: builtins.str,
            locale_id: builtins.str,
            invoked_by: typing.Optional[typing.Union["_IResolvable_da3f097b", typing.Union["CfnAppInstanceBot.InvokedByProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            responds_to: typing.Optional[builtins.str] = None,
            welcome_intent: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The configuration for an Amazon Lex V2 bot.

            :param lex_bot_alias_arn: The ARN of the Amazon Lex V2 bot's alias.
            :param locale_id: Identifies the Amazon Lex V2 bot's language and locale.
            :param invoked_by: Specifies the type of message that triggers a bot.
            :param responds_to: Determines whether the Amazon Lex V2 bot responds to all standard messages. Control messages are not supported.
            :param welcome_intent: The name of the welcome intent configured in the Amazon Lex V2 bot.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_chime as chime
                
                lex_configuration_property = chime.CfnAppInstanceBot.LexConfigurationProperty(
                    lex_bot_alias_arn="lexBotAliasArn",
                    locale_id="localeId",
                
                    # the properties below are optional
                    invoked_by=chime.CfnAppInstanceBot.InvokedByProperty(
                        standard_messages="standardMessages",
                        targeted_messages="targetedMessages"
                    ),
                    responds_to="respondsTo",
                    welcome_intent="welcomeIntent"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__59e9097c00a1cff69d67ed6937aea0b11010ff23c371f50b9ae25d98378dbf55)
                check_type(argname="argument lex_bot_alias_arn", value=lex_bot_alias_arn, expected_type=type_hints["lex_bot_alias_arn"])
                check_type(argname="argument locale_id", value=locale_id, expected_type=type_hints["locale_id"])
                check_type(argname="argument invoked_by", value=invoked_by, expected_type=type_hints["invoked_by"])
                check_type(argname="argument responds_to", value=responds_to, expected_type=type_hints["responds_to"])
                check_type(argname="argument welcome_intent", value=welcome_intent, expected_type=type_hints["welcome_intent"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "lex_bot_alias_arn": lex_bot_alias_arn,
                "locale_id": locale_id,
            }
            if invoked_by is not None:
                self._values["invoked_by"] = invoked_by
            if responds_to is not None:
                self._values["responds_to"] = responds_to
            if welcome_intent is not None:
                self._values["welcome_intent"] = welcome_intent

        @builtins.property
        def lex_bot_alias_arn(self) -> builtins.str:
            '''The ARN of the Amazon Lex V2 bot's alias.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html#cfn-chime-appinstancebot-lexconfiguration-lexbotaliasarn
            '''
            result = self._values.get("lex_bot_alias_arn")
            assert result is not None, "Required property 'lex_bot_alias_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def locale_id(self) -> builtins.str:
            '''Identifies the Amazon Lex V2 bot's language and locale.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html#cfn-chime-appinstancebot-lexconfiguration-localeid
            '''
            result = self._values.get("locale_id")
            assert result is not None, "Required property 'locale_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def invoked_by(
            self,
        ) -> typing.Optional[typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.InvokedByProperty"]]:
            '''Specifies the type of message that triggers a bot.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html#cfn-chime-appinstancebot-lexconfiguration-invokedby
            '''
            result = self._values.get("invoked_by")
            return typing.cast(typing.Optional[typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.InvokedByProperty"]], result)

        @builtins.property
        def responds_to(self) -> typing.Optional[builtins.str]:
            '''Determines whether the Amazon Lex V2 bot responds to all standard messages.

            Control messages are not supported.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html#cfn-chime-appinstancebot-lexconfiguration-respondsto
            '''
            result = self._values.get("responds_to")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def welcome_intent(self) -> typing.Optional[builtins.str]:
            '''The name of the welcome intent configured in the Amazon Lex V2 bot.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-chime-appinstancebot-lexconfiguration.html#cfn-chime-appinstancebot-lexconfiguration-welcomeintent
            '''
            result = self._values.get("welcome_intent")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LexConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceBotProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_instance_arn": "appInstanceArn",
        "configuration": "configuration",
        "metadata": "metadata",
        "name": "name",
        "tags": "tags",
    },
)
class CfnAppInstanceBotProps:
    def __init__(
        self,
        *,
        app_instance_arn: builtins.str,
        configuration: typing.Union["_IResolvable_da3f097b", typing.Union["CfnAppInstanceBot.ConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
        metadata: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_CfnTag_f6864754", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnAppInstanceBot``.

        :param app_instance_arn: The ARN of the AppInstance.
        :param configuration: A structure that contains configuration data.
        :param metadata: The metadata of the AppInstanceBot.
        :param name: The name of the AppInstanceBot.
        :param tags: The tags assigned to the AppInstanceBot.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_chime as chime
            
            cfn_app_instance_bot_props = chime.CfnAppInstanceBotProps(
                app_instance_arn="appInstanceArn",
                configuration=chime.CfnAppInstanceBot.ConfigurationProperty(
                    lex=chime.CfnAppInstanceBot.LexConfigurationProperty(
                        lex_bot_alias_arn="lexBotAliasArn",
                        locale_id="localeId",
            
                        # the properties below are optional
                        invoked_by=chime.CfnAppInstanceBot.InvokedByProperty(
                            standard_messages="standardMessages",
                            targeted_messages="targetedMessages"
                        ),
                        responds_to="respondsTo",
                        welcome_intent="welcomeIntent"
                    )
                ),
            
                # the properties below are optional
                metadata="metadata",
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d900ae3a9eb6a587e47f3e534920839a7bec4e3fc41d625d3e3b8eb9d31d4eae)
            check_type(argname="argument app_instance_arn", value=app_instance_arn, expected_type=type_hints["app_instance_arn"])
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_instance_arn": app_instance_arn,
            "configuration": configuration,
        }
        if metadata is not None:
            self._values["metadata"] = metadata
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def app_instance_arn(self) -> builtins.str:
        '''The ARN of the AppInstance.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html#cfn-chime-appinstancebot-appinstancearn
        '''
        result = self._values.get("app_instance_arn")
        assert result is not None, "Required property 'app_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration(
        self,
    ) -> typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.ConfigurationProperty"]:
        '''A structure that contains configuration data.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html#cfn-chime-appinstancebot-configuration
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast(typing.Union["_IResolvable_da3f097b", "CfnAppInstanceBot.ConfigurationProperty"], result)

    @builtins.property
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the AppInstanceBot.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html#cfn-chime-appinstancebot-metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the AppInstanceBot.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html#cfn-chime-appinstancebot-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_CfnTag_f6864754"]]:
        '''The tags assigned to the AppInstanceBot.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstancebot.html#cfn-chime-appinstancebot-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_CfnTag_f6864754"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAppInstanceBotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_chime.CfnAppInstanceProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "metadata": "metadata", "tags": "tags"},
)
class CfnAppInstanceProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        metadata: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["_CfnTag_f6864754", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnAppInstance``.

        :param name: The name of the AppInstance.
        :param metadata: The metadata of the AppInstance. Limited to a 1KB string in UTF-8.
        :param tags: Tags assigned to the AppInstance.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstance.html
        :exampleMetadata: fixture=_generated

        Example::

            from aws_cdk import CfnTag
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_chime as chime
            
            cfn_app_instance_props = chime.CfnAppInstanceProps(
                name="name",
            
                # the properties below are optional
                metadata="metadata",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551f6928f9d6a158547ebe3a9d4b368b45ad66d983bfb330b063b77c078ca90e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if metadata is not None:
            self._values["metadata"] = metadata
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the AppInstance.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstance.html#cfn-chime-appinstance-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metadata(self) -> typing.Optional[builtins.str]:
        '''The metadata of the AppInstance.

        Limited to a 1KB string in UTF-8.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstance.html#cfn-chime-appinstance-metadata
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List["_CfnTag_f6864754"]]:
        '''Tags assigned to the AppInstance.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-chime-appinstance.html#cfn-chime-appinstance-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List["_CfnTag_f6864754"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAppInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnAppInstance",
    "CfnAppInstanceBot",
    "CfnAppInstanceBotProps",
    "CfnAppInstanceProps",
]

publication.publish()

def _typecheckingstub__6d337d6c149cc789c0b6f05ba4ba90f831464295606b004354b7815daaed0c77(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    metadata: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_CfnTag_f6864754, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f74b0e7014ea5c23e28103a5fb5867813697fd8201279c330a3aa769bc126a1(
    resource: _IAppInstanceRef_43d18bab,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a664656abafe2adc6e2a0a9db5e06dc33b5b3b6a0fa2a5ca0b61b7b95d0c32(
    x: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400a60274a57ac76d314b93fb263163beba6942cc730e90588d6f74e739f4eb0(
    inspector: _TreeInspector_488e0dd5,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c4ccf5db0f869956272a9d89ee82b1cfb49e2aacbbc94b43a595151f8b37e60(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b72de3b84f85f89b400c53dced98e7828184761f13429f1028134b5727fe38e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4d28a89759474ddf9cf296e1da1bbf9afe7e7c1413d9a4d175db15deaca419f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc357af54a794ca273668787f93dac3a63d2f85c8108d86aa56926b60d6aac5a(
    value: typing.Optional[typing.List[_CfnTag_f6864754]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca75944f6ceb69180d3b0f352517267777aeee7ffaa12b2f1a465cf9b6a3e00(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    app_instance_arn: builtins.str,
    configuration: typing.Union[_IResolvable_da3f097b, typing.Union[CfnAppInstanceBot.ConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    metadata: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_CfnTag_f6864754, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49c5faf3dcf2887594ff746db96b49d9757db79f86e9d6f358d9f275ee8c8210(
    resource: _IAppInstanceBotRef_519ced67,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0255372b69a195b0351367c082f9533519223c17e242b93716f61ed8e55dea62(
    x: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427e24f474e9d78b560301eb631ab4ec523303c4565f63f29c83299fe5abafb1(
    inspector: _TreeInspector_488e0dd5,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f31284f1d604da54c34b53acb2ff3863b786fb7370f15d19da68df814cd8ad(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a53900f75f263ec868d4efe44340a9273169b155a8e54a68fe8cde3818baec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d36a14f99ec95cd590d6c1757bb41c8b9235cf6b317fa73e6692074ed033195a(
    value: typing.Union[_IResolvable_da3f097b, CfnAppInstanceBot.ConfigurationProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45024baca15a880d713b7458c08c15471a9b4b4bc485fcaa496535c2d75a30a8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ad6a83eab879d92eb2609e2f37735b3c2383bb2e7e24c6cefbec192e42c39e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d87e45b7d9459784717058ca252a094c146e5656ea14d9da51f1cf05f4aa56d4(
    value: typing.Optional[typing.List[_CfnTag_f6864754]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09ff343ee28319a719419e7819c467b339964da524abd8a8f50f44edd43b11a8(
    *,
    lex: typing.Union[_IResolvable_da3f097b, typing.Union[CfnAppInstanceBot.LexConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a8291bb53d368f6b1012fdd17317226c377241787e7d74d9371e641c527be4(
    *,
    standard_messages: builtins.str,
    targeted_messages: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59e9097c00a1cff69d67ed6937aea0b11010ff23c371f50b9ae25d98378dbf55(
    *,
    lex_bot_alias_arn: builtins.str,
    locale_id: builtins.str,
    invoked_by: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Union[CfnAppInstanceBot.InvokedByProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    responds_to: typing.Optional[builtins.str] = None,
    welcome_intent: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d900ae3a9eb6a587e47f3e534920839a7bec4e3fc41d625d3e3b8eb9d31d4eae(
    *,
    app_instance_arn: builtins.str,
    configuration: typing.Union[_IResolvable_da3f097b, typing.Union[CfnAppInstanceBot.ConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    metadata: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_CfnTag_f6864754, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551f6928f9d6a158547ebe3a9d4b368b45ad66d983bfb330b063b77c078ca90e(
    *,
    name: builtins.str,
    metadata: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_CfnTag_f6864754, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
