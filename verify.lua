core.register_fetches("verify_access", function(txn, api)
    -- env(api) check is kept for backwards compatibility
    local read_allowed = txn.f:env(api) == "1" or txn.f:env(api .. "_READ") == "1"
    -- env(POST) check is kept for backwards compatibility
    local write_allowed = txn.f:env(api .. "_WRITE") == "1" or (read_allowed and txn.f:env("POST") == "1")
    local method = txn.f:method()

    local result = ((method == "GET" or method == "HEAD") and read_allowed)
        or ((method ~= "GET" and method ~= "HEAD") and write_allowed)

    return result
end)
