"""Separate pinned task policy from native Shinka's varying prompt suffix."""
def cleave(request, prefix):
    messages=request.get('messages')
    if not isinstance(prefix,str) or not prefix or not isinstance(messages,list) or not messages:
        raise ValueError('CONTEXT_PREFIX_MISSING')
    first=messages[0]
    if first.get('role')!='system' or not isinstance(first.get('content'),str) or not first['content'].startswith(prefix):
        raise ValueError('CONTEXT_PREFIX_CHANGED')
    suffix=first['content'][len(prefix):]
    # Preserve both content and instruction roles; only the cache boundary moves.
    return {**request,'messages':[{'role':'system','content':prefix}]+([{'role':'system','content':suffix}] if suffix else [])+messages[1:]}
