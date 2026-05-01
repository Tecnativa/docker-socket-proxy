-- Strips the Env array from Docker container inspect responses so that
-- environment variables (which often carry secrets) are never forwarded
-- to clients, even when CONTAINERS=1 is set.
core.register_action("remove_env", {"http-res"}, function(txn)
    local body = txn.res.body:data()
    if not body or #body == 0 then
        return
    end
    local new_body = body:gsub('"Env"%s*:%s*%b[]', '"Env":[]')
    if new_body ~= body then
        txn.res.body:remove(0, #body)
        txn.res.body:append(new_body)
        txn.res.http:del_header("content-length")
        txn.res.http:add_header("content-length", tostring(#new_body))
    end
end)