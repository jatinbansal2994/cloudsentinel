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

from ..._jsii import *

import constructs as _constructs_77d1e7e8
from .. import IEnvironmentAware as _IEnvironmentAware_f39049ee


@jsii.data_type(
    jsii_type="aws-cdk-lib.interfaces.aws_chime.AppInstanceBotReference",
    jsii_struct_bases=[],
    name_mapping={"app_instance_bot_arn": "appInstanceBotArn"},
)
class AppInstanceBotReference:
    def __init__(self, *, app_instance_bot_arn: builtins.str) -> None:
        '''A reference to a AppInstanceBot resource.

        :param app_instance_bot_arn: The AppInstanceBotArn of the AppInstanceBot resource.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.interfaces import aws_chime as interfaces_chime
            
            app_instance_bot_reference = interfaces_chime.AppInstanceBotReference(
                app_instance_bot_arn="appInstanceBotArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d94314e184ef238bc15359652813db5a17decbc7880453c10eebfdb5aee1574b)
            check_type(argname="argument app_instance_bot_arn", value=app_instance_bot_arn, expected_type=type_hints["app_instance_bot_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_instance_bot_arn": app_instance_bot_arn,
        }

    @builtins.property
    def app_instance_bot_arn(self) -> builtins.str:
        '''The AppInstanceBotArn of the AppInstanceBot resource.'''
        result = self._values.get("app_instance_bot_arn")
        assert result is not None, "Required property 'app_instance_bot_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstanceBotReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.interfaces.aws_chime.AppInstanceReference",
    jsii_struct_bases=[],
    name_mapping={"app_instance_arn": "appInstanceArn"},
)
class AppInstanceReference:
    def __init__(self, *, app_instance_arn: builtins.str) -> None:
        '''A reference to a AppInstance resource.

        :param app_instance_arn: The AppInstanceArn of the AppInstance resource.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.interfaces import aws_chime as interfaces_chime
            
            app_instance_reference = interfaces_chime.AppInstanceReference(
                app_instance_arn="appInstanceArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7a63f08f74043f81dd278aff7af9a1fbed0722dd9d181168266b0223b7dd9a)
            check_type(argname="argument app_instance_arn", value=app_instance_arn, expected_type=type_hints["app_instance_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_instance_arn": app_instance_arn,
        }

    @builtins.property
    def app_instance_arn(self) -> builtins.str:
        '''The AppInstanceArn of the AppInstance resource.'''
        result = self._values.get("app_instance_arn")
        assert result is not None, "Required property 'app_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppInstanceReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="aws-cdk-lib.interfaces.aws_chime.IAppInstanceBotRef")
class IAppInstanceBotRef(
    _constructs_77d1e7e8.IConstruct,
    _IEnvironmentAware_f39049ee,
    typing_extensions.Protocol,
):
    '''(experimental) Indicates that this resource can be referenced as a AppInstanceBot.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="appInstanceBotRef")
    def app_instance_bot_ref(self) -> "AppInstanceBotReference":
        '''(experimental) A reference to a AppInstanceBot resource.

        :stability: experimental
        '''
        ...


class _IAppInstanceBotRefProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_IEnvironmentAware_f39049ee), # type: ignore[misc]
):
    '''(experimental) Indicates that this resource can be referenced as a AppInstanceBot.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.interfaces.aws_chime.IAppInstanceBotRef"

    @builtins.property
    @jsii.member(jsii_name="appInstanceBotRef")
    def app_instance_bot_ref(self) -> "AppInstanceBotReference":
        '''(experimental) A reference to a AppInstanceBot resource.

        :stability: experimental
        '''
        return typing.cast("AppInstanceBotReference", jsii.get(self, "appInstanceBotRef"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAppInstanceBotRef).__jsii_proxy_class__ = lambda : _IAppInstanceBotRefProxy


@jsii.interface(jsii_type="aws-cdk-lib.interfaces.aws_chime.IAppInstanceRef")
class IAppInstanceRef(
    _constructs_77d1e7e8.IConstruct,
    _IEnvironmentAware_f39049ee,
    typing_extensions.Protocol,
):
    '''(experimental) Indicates that this resource can be referenced as a AppInstance.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="appInstanceRef")
    def app_instance_ref(self) -> "AppInstanceReference":
        '''(experimental) A reference to a AppInstance resource.

        :stability: experimental
        '''
        ...


class _IAppInstanceRefProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_IEnvironmentAware_f39049ee), # type: ignore[misc]
):
    '''(experimental) Indicates that this resource can be referenced as a AppInstance.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.interfaces.aws_chime.IAppInstanceRef"

    @builtins.property
    @jsii.member(jsii_name="appInstanceRef")
    def app_instance_ref(self) -> "AppInstanceReference":
        '''(experimental) A reference to a AppInstance resource.

        :stability: experimental
        '''
        return typing.cast("AppInstanceReference", jsii.get(self, "appInstanceRef"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAppInstanceRef).__jsii_proxy_class__ = lambda : _IAppInstanceRefProxy


__all__ = [
    "AppInstanceBotReference",
    "AppInstanceReference",
    "IAppInstanceBotRef",
    "IAppInstanceRef",
]

publication.publish()

def _typecheckingstub__d94314e184ef238bc15359652813db5a17decbc7880453c10eebfdb5aee1574b(
    *,
    app_instance_bot_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7a63f08f74043f81dd278aff7af9a1fbed0722dd9d181168266b0223b7dd9a(
    *,
    app_instance_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IAppInstanceBotRef, IAppInstanceRef]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
