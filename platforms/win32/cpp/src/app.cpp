#include "precompiled.h"
#include "app.h"
#include "appres.h"
#include "zip.h"

#define QUOTE(x) #x
#define STRING(x) QUOTE(x)

auto zip_unpack_from_buffer(std::span<uint8_t> const buffer, std::filesystem::path const& out_path) -> void {
    zip_source_t* zip_source = zip_source_buffer_create(buffer.data(), buffer.size(), 0, nullptr);

    if(zip_source) {
        zip_t* zip = zip_open_from_source(zip_source, ZIP_RDONLY, nullptr);
        std::vector<uint8_t> buffer_data(8192);

        uint32_t file_count = static_cast<uint32_t>(zip_get_num_entries(zip, 0));
        for(uint32_t i = 0; i < file_count; ++i) {
            zip_stat_t stat;
            if(zip_stat_index(zip, i, 0, &stat)) {
                throw std::runtime_error("Unexpected error unpacking archive");
            }
                
            if(stat.valid & (ZIP_STAT_NAME | ZIP_STAT_SIZE)) {
                zip_file* file = zip_fopen_index(zip, i, 0);
                if(!file) {
                    throw std::runtime_error("Unexpected error unpacking archive");
                }

                if(!std::filesystem::exists(out_path / std::filesystem::path(stat.name).parent_path())) {
                    std::filesystem::create_directory(out_path / std::filesystem::path(stat.name).parent_path());
                }

                std::fstream fs(out_path / stat.name, std::ios::out | std::ios::binary);

                uint64_t read_bytes = 0;
                do {
                    read_bytes = zip_fread(file, buffer_data.data(), buffer_data.size());
                    if(read_bytes > 0) {
                        fs.write(reinterpret_cast<char*>(buffer_data.data()), read_bytes);
                    }
                } while(read_bytes > 0);
                zip_fclose(file);
            }
        }
        zip_close(zip);
    } else {
        throw std::runtime_error("Unexpected error unpacking archive");
    }
    zip_source_close(zip_source);
}

auto App::check_install() -> bool {
    std::filesystem::path const internal_path = std::filesystem::current_path();
    std::filesystem::path const app_path = internal_path / ".app";

    if(!std::filesystem::exists(app_path / ".VERSION")) {
        return false;
    }

    std::ifstream ifs(app_path / ".VERSION");
    std::string buffer((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());

    if(buffer.compare(STRING(BUILD_VERSION)) != 0) {
        return false;
    }
    return true;
}

auto App::install() -> void {
    std::filesystem::path const internal_path = std::filesystem::current_path();
    std::filesystem::path const app_path = internal_path / ".app";

    if(std::filesystem::exists(app_path)) {
        std::filesystem::remove_all(app_path);
    }

    if(!std::filesystem::exists(app_path)) {
        std::filesystem::create_directory(app_path);
        ::SetFileAttributes(app_path.string().c_str(), FILE_ATTRIBUTE_HIDDEN);
    }

    {
        HRSRC source = ::FindResource(::GetModuleHandle(nullptr), MAKEINTRESOURCE(IDB_APP), RT_RCDATA);
        HGLOBAL resource = ::LoadResource(::GetModuleHandle(nullptr), source);

        try {
            zip_unpack_from_buffer(
                std::span<uint8_t>(reinterpret_cast<uint8_t*>(::LockResource(resource)), ::SizeofResource(::GetModuleHandle(nullptr), source)),
                app_path
            );
        } catch(std::runtime_error e) {
            std::filesystem::remove_all(app_path);
            throw e;
        }
    }
}
