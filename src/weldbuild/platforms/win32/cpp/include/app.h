#pragma  once

#include <Windows.h>

class App {
public:
    App() = default;

    auto check_install() -> bool;

    auto install() -> void;
};

auto zip_unpack_from_buffer(std::span<uint8_t> const buffer, std::filesystem::path const& out_path) -> void;
