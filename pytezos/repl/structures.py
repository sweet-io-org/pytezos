from pytezos.michelson.forge import pack
from pytezos.repl.control import instruction
from pytezos.repl.context import Context
from pytezos.repl.types import assert_stack_type, Option, Pair, String, Bytes, List, BigMap, Map, Set, Or, Bool, Nat, \
    Unit, StackItem, dispatch_type_map


@instruction(['CAR', 'CDR'])
def do_car(ctx: Context, prim, args, annots):
    top = ctx.pop()
    assert_stack_type(top, Pair)
    handlers = {
        'CAR': lambda x: x[0],
        'CDR': lambda x: x[1]
    }
    res = handlers[prim](list(iter(top)))
    return ctx.ins(res, annots=annots)


@instruction('CONCAT')
def do_concat(ctx: Context, prim, args, annots):
    top = ctx.pop()
    assert_stack_type(top, [String, Bytes, List])
    if type(top) in [String, Bytes]:
        second = ctx.pop()
        val_type = dispatch_type_map(top, second, {
            (String, String): str,
            (Bytes, Bytes): bytes
        })
        res = type(top)(val_type(top) + val_type(second))
    elif type(top) == List:
        res_type = top.val_type()
        val_type, sep = {String: (str, ''), Bytes: (bytes, b'')}[res_type]
        res = res_type(sep.join(map(val_type, top)))
    else:
        assert False
    return ctx.ins(res, annots=annots)


@instruction('CONS')
def do_cons(ctx: Context, prim, args, annots):
    val, container = ctx.pop2()
    assert_stack_type(container, List)
    res = container.prepend(val)
    return ctx.ins(res, annots=annots)


@instruction('EMPTY_BIG_MAP', args_len=2)
def do_empty_big_map(ctx: Context, prim, args, annots):
    res = BigMap.empty(k_type_expr=args[0], v_type_expr=args[1])
    return ctx.ins(res, annots=annots)


@instruction('EMPTY_MAP', args_len=2)
def do_empty_map(ctx: Context, prim, args, annots):
    res = Map.empty(k_type_expr=args[0], v_type_expr=args[1])
    return ctx.ins(res, annots=annots)


@instruction('EMPTY_SET', args_len=1)
def do_empty_set(ctx: Context, prim, args, annots):
    res = Set.empty(k_type_expr=args[0])
    return ctx.ins(res, annots=annots)


@instruction('GET')
def do_get(ctx: Context, prim, args, annots):
    key, container = ctx.pop2()
    assert_stack_type(container, [Map, BigMap])
    if key in container:
        val = next(v for k, v in container if k == key)
        res = Option.some(val)
    else:
        res = Option.none(container.val_type_expr())
    return ctx.ins(res, annots=annots)


@instruction(['LEFT', 'RIGHT'], args_len=1)
def do_left(ctx: Context, prim, args, annots):
    top = ctx.pop()
    if prim == 'LEFT':
        res = Or.left(r_type_expr=args[0], item=top)
    else:
        res = Or.right(l_type_expr=args[0], item=top)
    return ctx.ins(res, annots=annots)


@instruction('MEM')
def do_mem(ctx: Context, prim, args, annots):
    key, container = ctx.pop2()
    assert_stack_type(container, [Set, Map, BigMap])
    res = Bool(key in container)
    return ctx.ins(res, annots=annots)


@instruction('NIL', args_len=1)
def do_nil(ctx: Context, prim, args, annots):
    nil = List.empty(args[0])
    return ctx.ins(nil, annots=annots)


@instruction('NONE', args_len=1)
def do_none(ctx: Context, prim, args, annots):
    none = Option.none(args[0])
    return ctx.ins(none, annots=annots)


@instruction('PACK')
def do_pack(ctx: Context, prim, args, annots):
    top = ctx.pop()
    res = Bytes(pack(top.val_node))
    return ctx.ins(res, annots=annots)


@instruction('PAIR')
def do_pair(ctx: Context, prim, args, annots):
    left, right = ctx.pop2()
    res = Pair.new(left, right)
    return ctx.ins(res, annots=annots)


@instruction('SIZE')
def do_size(ctx: Context, prim, args, annots):
    top = ctx.pop()
    assert_stack_type(top, [String, Bytes, List, Set, Map])
    res = Nat(len(top))
    return ctx.ins(res, annots=annots)


@instruction('SLICE')
def do_slice(ctx: Context, prim, args, annots):
    offset, length, s = ctx.pop3()
    assert_stack_type(s, [String, Bytes])
    if offset + length < len(s):
        sls = str(s)[offset:offset + length]
        res = Option.some(type(s)(sls))
    else:
        res = Option.none(type(s)().type_expr)
    return ctx.ins(res, annots=annots)


@instruction('SOME')
def do_some(ctx: Context, prim, args, annots):
    top = ctx.pop()
    res = Option.some(top)
    return ctx.ins(res, annots=annots)


@instruction('UNIT')
def do_unit(ctx: Context, prim, args, annots):
    return ctx.ins(Unit(), annots=annots)


@instruction('UNPACK', args_len=1)
def do_unpack(ctx: Context, prim, args, annots):
    top = ctx.pop()
    assert_stack_type(top, Bytes)
    # TODO: unpack micheline
    res = StackItem.parse(type_expr=args[0], val_expr=None)
    return ctx.ins(res, annots=annots)


@instruction('UPDATE')
def do_update(ctx: Context, prim, args, annots):
    key, val, container = ctx.pop3()
    assert_stack_type(container, [Set, Map, BigMap])

    if type(container) == Set:
        assert_stack_type(val, Bool)
        if val:
            res = container.add(key)
        else:
            res = Set.new(list(filter(lambda x: x != key, container)))
    else:
        assert_stack_type(val, Option)
        if val.is_none():
            res = type(container).new(list(filter(lambda x: x[0] != key, container)))
        else:
            res = container.add(key, next(iter(val)))

    return ctx.ins(res, annots=annots)